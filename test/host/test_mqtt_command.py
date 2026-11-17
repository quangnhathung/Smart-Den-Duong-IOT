"""Offline command fixture tests; does not connect to a broker."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr

SPEC = importlib.util.spec_from_file_location('mqtt_command', Path(__file__).resolve().parents[2] / 'scripts/mqtt-command.py')
CLIENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT)


class CommandFixtureChecks(unittest.TestCase):
    def setUp(self):
        self.telemetry = dict(schema_version=1, node_id='node_01', boot_id='b7e28a10', uptime_ms=5000000000)

    def test_valid_modes_deadline_and_id(self):
        manual = CLIENT.make_command(self.telemetry, 'MANUAL', 80)
        self.assertEqual(manual['deadline_uptime_ms'], 5000005000)
        self.assertEqual(manual['brightness'], 80)
        self.assertEqual(CLIENT.uuid.UUID(manual['command_id']).version, 4)
        self.assertNotIn('brightness', CLIENT.make_command(self.telemetry, 'AUTO'))

    def test_invalid_arguments(self):
        for mode, brightness in [('AUTO', 80), ('MANUAL', None), ('MANUAL', True), ('MANUAL', 101), ('INVALID', None)]:
            with self.assertRaises(ValueError):
                CLIENT.make_command(self.telemetry, mode, brightness)
        for value in [True, -1, 1.5, (1 << 64) - 1]:
            with self.assertRaises(ValueError):
                CLIENT.make_command(dict(self.telemetry, uptime_ms=value), 'AUTO')

    def test_fault_cases(self):
        self.assertEqual(CLIENT.make_command(self.telemetry, 'AUTO', case='expired')['deadline_uptime_ms'], 0)
        self.assertNotEqual(CLIENT.make_command(self.telemetry, 'AUTO', case='wrong-boot')['boot_id'], self.telemetry['boot_id'])
        self.assertEqual(CLIENT.make_command(self.telemetry, 'AUTO', case='wrong-node')['node_id'], 'node_02')
        self.assertEqual(CLIENT.make_command(self.telemetry, 'AUTO', case='invalid-brightness')['brightness'], 101)

    def test_three_node_destinations_and_wrong_node_cases(self):
        for node in CLIENT.NODE_IDS:
            telemetry = dict(self.telemetry, node_id=node)
            result = CLIENT.make_command(telemetry, 'AUTO', node=node)
            self.assertEqual(result['node_id'], node)
            self.assertNotEqual(CLIENT.make_command(telemetry, 'AUTO', case='wrong-node', node=node)['node_id'], node)
            other = next(n for n in CLIENT.NODE_IDS if n != node)
            with self.assertRaises(ValueError):
                CLIENT.make_command(telemetry, 'AUTO', node=other)
        with self.assertRaises(ValueError):
            CLIENT.make_command(self.telemetry, 'AUTO', node='node_04')

    def test_cli_selects_node(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'telemetry.json'
            for node in CLIENT.NODE_IDS:
                path.write_text(json.dumps(dict(self.telemetry, node_id=node)))
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(CLIENT.main(['--telemetry', str(path), '--mode', 'AUTO', '--node', node]), 0)
                self.assertEqual(json.loads(output.getvalue())['node_id'], node)

    def test_cli_requires_fresh_capture(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'telemetry.json'
            path.write_text(json.dumps(self.telemetry), encoding='utf-8')
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(CLIENT.main(['--telemetry', str(path), '--mode', 'AUTO']), 0)
            self.assertEqual(json.loads(output.getvalue())['mode'], 'AUTO')
            for age in [4, -1]:
                with patch.object(CLIENT.time, 'time', return_value=path.stat().st_mtime + age), redirect_stderr(io.StringIO()):
                    self.assertEqual(CLIENT.main(['--telemetry', str(path), '--mode', 'AUTO']), 1)


if __name__ == '__main__':
    unittest.main()
