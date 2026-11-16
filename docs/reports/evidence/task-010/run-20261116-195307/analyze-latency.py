"""Summarize real capture; keep invalid captures separate from acceptance samples."""
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / 'latency-events-20261116-201020.jsonl'
events = [json.loads(line) for line in EVENTS.read_text(encoding='utf8').splitlines() if line.strip()]
for derived in sorted(ROOT.glob('trial-*-derived-action.json')):
    value = json.loads(derived.read_text(encoding='utf8'))
    assert value['source'] == 'evidence-analysis'
    assert value['first_new'] in events and value['previous'] in events
    events.append(value)


def offset(source, page_id=None):
    values = [e for e in events if e['event'] == 'clock-sync' and e['source'] == source
              and (page_id is None or e.get('page_id') == page_id)]
    if not values:
        return None
    sample = min(values[-1]['samples'], key=lambda x: x['rtt_ms'])
    return sample['offset_low_ms'], sample['offset_high_ms']


rows = []
for trial_id in range(1, 11):
    actions = [e for e in events if e['event'] == 'sensor-action-observed' and e.get('trial_id') == trial_id]
    renders = [e for e in events if e['event'] == 'render-match' and e.get('trial', {}).get('id') == trial_id]
    markers = [e for e in events if e['event'] == 'manual-start-marker' and e.get('trial', {}).get('id') == trial_id]
    renders = [r for r in renders if not r.get('trial', {}).get('require_marker') or any(
        m.get('page_id') == r.get('page_id')
        and m.get('trial', {}).get('revision') == r.get('trial', {}).get('revision')
        and m['marker_ms'] <= r['render_ms'] for m in markers)]
    if not actions and markers and renders:
        render = renders[-1]
        marker = next((e for e in reversed(markers) if e.get('page_id') == render.get('page_id')), None)
        if marker:
            bo = offset('browser', marker['page_id'])
            if bo:
                start = marker['marker_ms'] + bo[0]
                target = marker['trial']['target_cm']
                samples = [e for e in events if e['source'] == 'mqtt' and e['event'] == 'message'
                           and e.get('topic', '').endswith('/telemetry')
                           and e.get('body', {}).get('boot_id') == marker['trial']['boot_at_arm']
                           and e['host_ms'] >= marker['marker_ms'] + bo[1]
                           and str(e.get('body', {}).get('seq', '')).isdigit()
                           and int(e['body']['seq']) > int(marker['trial']['seq_at_arm'])
                           and isinstance(e['body'].get('distance_cm'), (int, float))
                           and abs(e['body']['distance_cm'] - target) <= max(2, target * .05)]
                if samples:
                    sample = min(samples, key=lambda e: e['host_ms'])
                    actions = [dict(source='evidence-analysis', event='sensor-action-observed',
                                    trial_id=trial_id, action_low_ms=start, action_high_ms=sample['host_ms'],
                                    host_clock=True, marker=marker, first_changed_sample=sample,
                                    method='Action interval: browser marker lower bound to first changed real MQTT sample upper bound; not an exact action timestamp')]
    if not actions or not renders:
        rows.append(dict(trial_id=trial_id, status='PENDING', reason='Missing action or matching render'))
        continue
    action, render = actions[-1], renders[-1]
    page_id = render.get('page_id')
    reasons = []
    if not page_id:
        reasons.append('Browser events have no page identity')
    browser_offset = offset('browser', page_id) if page_id else None
    observer_offset = (0, 0) if action.get('host_clock') else offset('node-ui-observer')
    if browser_offset is None or observer_offset is None or action.get('action_low_ms') is None:
        reasons.append('Missing clock calibration or action lower bound')
    row = dict(trial_id=trial_id, page_id=page_id, key=render['key'], sensor_action=action,
               render=render, status='INCOMPLETE')
    if browser_offset and observer_offset and action.get('action_low_ms') is not None:
        action_low = action['action_low_ms'] + observer_offset[0]
        action_high = action['action_high_ms'] + observer_offset[1]
        render_low = render['render_ms'] + browser_offset[0]
        render_high = render['render_ms'] + browser_offset[1]
        row['action_host_interval_ms'] = [action_low, action_high]
        row['render_host_interval_ms'] = [render_low, render_high]
        row['latency_interval_ms'] = [render_low - action_high, render_high - action_low]
        page_events = sorted([e for e in events if e.get('page_id') == page_id], key=lambda e: e['browser_ms'])
        prior = [e for e in page_events if e['browser_ms'] + browser_offset[1] <= action_low]
        during = [e for e in page_events if action_low <= e['browser_ms'] + browser_offset[1]
                  and e['browser_ms'] + browser_offset[0] <= render_high]
        if not prior or prior[-1].get('visibility') != 'visible':
            reasons.append('Page visibility not established at action start')
        if any(e.get('visibility') == 'hidden' for e in during):
            reasons.append('Measurement page hidden during trial')
        mqtt = [e for e in events if e['source'] == 'mqtt' and e['event'] == 'message'
                and e.get('body', {}).get('boot_id') == render['telemetry']['boot_id']
                and str(e.get('body', {}).get('seq')) == str(render['telemetry']['seq'])]
        row['mqtt'] = mqtt[0] if mqtt else None
        if not mqtt:
            reasons.append('Missing matching live MQTT packet')
        marker = action.get('marker')
        if marker:
            if not marker.get('baseline'):
                reasons.append('Missing sensor baseline captured at start marker')
            if mqtt and mqtt[0]['host_ms'] <= marker['marker_ms'] + browser_offset[1]:
                reasons.append('Rendered MQTT sample predates start marker; not a new sensor transition')
                row['invalid_descriptive_interval_ms'] = row.pop('latency_interval_ms')
            if marker.get('baseline') and int(render['telemetry']['seq']) <= int(marker['baseline']['seq']):
                reasons.append('Rendered sequence is not newer than marker baseline')
        if not reasons:
            lo, hi = row['latency_interval_ms']
            row['status'] = 'PASS' if hi <= 3000 and lo >= 0 else 'FAIL' if lo > 3000 else 'INCOMPLETE'
            if row['status'] == 'INCOMPLETE':
                reasons.append('Uncertainty crosses threshold or inconsistent timing')
    row['reasons'] = reasons
    rows.append(row)

valid = [r['latency_interval_ms'] for r in rows if r['status'] in ('PASS', 'FAIL')]
summary = dict(generated_at=datetime.now(timezone.utc).isoformat(), source=EVENTS.name,
               threshold_ms=3000, valid_samples=len(valid), required_samples=10, rows=rows,
               median_interval_ms=[statistics.median(x[i] for x in valid) for i in (0, 1)] if valid else None,
               max_interval_ms=[max(x[i] for x in valid) for i in (0, 1)] if valid else None,
               note='Two rAF is a browser rendering proxy, not a screen photon measurement. No fixture or MQTT publish.')
(ROOT / 'latency-progress.json').write_text(json.dumps(summary, indent=2), encoding='utf8')
print(json.dumps({k: summary[k] for k in ('valid_samples', 'median_interval_ms', 'max_interval_ms')}))
print(json.dumps([dict(trial_id=r['trial_id'], status=r['status'], reasons=r.get('reasons')) for r in rows]))
