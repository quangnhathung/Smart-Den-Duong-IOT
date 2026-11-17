#!/usr/bin/env python3
"""Prepare selected Wokwi artifacts from their matching PlatformIO environments."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

NODE_ENVIRONMENTS = {'node_01': 'esp32dev', 'node_02': 'node_02', 'node_03': 'node_03'}
ARTIFACTS = ('firmware.bin', 'firmware.elf')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(root, node='node_01'):
    if node not in (*NODE_ENVIRONMENTS, 'all'):
        raise ValueError('Unknown node')
    selected = tuple(NODE_ENVIRONMENTS) if node == 'all' else (node,)
    inputs = [root / 'platformio.ini']
    for folder in ('src', 'include', 'lib'):
        inputs.extend(p for p in (root / folder).rglob('*') if p.is_file())
    newest = max(p.stat().st_mtime_ns for p in inputs)
    # Validate all selected sources before copying anything, so partial preparation is not reported as success.
    for name in selected:
        environment = NODE_ENVIRONMENTS[name]
        for artifact in ARTIFACTS:
            source = root / '.pio/build' / environment / artifact
            if not source.is_file() or not source.stat().st_size:
                raise RuntimeError(f'Missing or empty artifact: {source}; build {environment} first')
            if source.stat().st_mtime_ns < newest:
                raise RuntimeError(f'Artifacts are older than project inputs; build {environment} successfully first')
    results = []
    for name in selected:
        environment = NODE_ENVIRONMENTS[name]
        destination = root / 'simulations' / name / 'build'
        destination.mkdir(parents=True, exist_ok=True)
        manifest = {'node_id': name, 'environment': environment,
                    'identity_verification': 'Expected identity from environment; confirm via live Serial/MQTT',
                    'inputs_sha256': {str(p.relative_to(root)): digest(p) for p in sorted(inputs)}, 'artifacts': {}}
        for artifact in ARTIFACTS:
            source = root / '.pio/build' / environment / artifact
            target = destination / artifact
            shutil.copy2(source, target)
            checksum = digest(source)
            if digest(target) != checksum:
                raise RuntimeError(f'Checksum mismatch: {target}')
            manifest['artifacts'][artifact] = {'source': str(source.relative_to(root)),
                                              'target': str(target.relative_to(root)), 'sha256': checksum}
            print(f'{name} {artifact} SHA-256 {checksum}')
        (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        results.append(manifest)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node', choices=(*NODE_ENVIRONMENTS, 'all'), default='node_01')
    args = parser.parse_args(argv)
    try:
        prepare(Path(__file__).resolve().parents[1], args.node)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
