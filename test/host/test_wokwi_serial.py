"""Offline tests of the RFC2217 command verifier, not a Wokwi live test."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock
from contextlib import redirect_stdout
import io
import tempfile
import types

MODULE = Path(__file__).resolve().parents[2] / 'scripts/wokwi-serial.py'
SPEC = importlib.util.spec_from_file_location('wokwi_serial', MODULE)
CLIENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT)


def control(uptime, mode='MANUAL', applied=80, mqtt=1, target=80):
    return f'CONTROL uptime_ms={uptime} mode={mode} target={target} applied={applied} mqtt={mqtt}'


class VerificationChecks(unittest.TestCase):
    def test_acceptance_required_and_applied(self):
        check = CLIENT.Verification('MANUAL', 80)
        self.assertFalse(check.observe(control(1000)))
        check.observe('LOCAL command accepted=1; use AUTO or MANUAL')
        self.assertFalse(check.observe(control(2000, applied=40)))
        self.assertTrue(check.observe(control(3000)))

    def test_auto(self):
        check = CLIENT.Verification('AUTO')
        check.observe('LOCAL command accepted=1')
        self.assertTrue(check.observe(control(3000, mode='AUTO')))

    def test_manual_timeout(self):
        check = CLIENT.Verification('MANUAL', 80, True)
        check.observe('LOCAL command accepted=1')
        self.assertFalse(check.observe(control(1000)))
        self.assertTrue(check.observe(control(61000, mode='AUTO')))

    def test_early_fallback_and_offline_are_not_timeout_pass(self):
        for line in [control(2000, mode='AUTO'), control(61000, mode='AUTO', mqtt=0)]:
            check = CLIENT.Verification('MANUAL', 80, True)
            check.observe('LOCAL command accepted=1')
            check.observe(control(1000))
            with self.assertRaises(ValueError):
                check.observe(line)

    def test_reject_restart_and_uptime_decrease(self):
        for line in ['LOCAL command accepted=0', 'P2/A2 lighting control', control(500)]:
            check = CLIENT.Verification('MANUAL', 80, True)
            check.observe('LOCAL command accepted=1')
            check.observe(control(1000))
            with self.assertRaises(ValueError):
                check.observe(line)

    def test_second_command_invalidates_timeout(self):
        check = CLIENT.Verification('MANUAL', 80, True)
        check.observe('LOCAL command accepted=1')
        with self.assertRaises(ValueError):
            check.observe('LOCAL command accepted=1')

    def test_cli_sends_newline_and_captures_reply(self):
        class Connection:
            def __init__(self, response):
                self.response = bytearray(response.encode('ascii'))
                self.sent = None

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def write(self, data):
                self.sent = data
                return len(data)

            def read(self, _):
                return bytes([self.response.pop(0)]) if self.response else b''

        for args, expected, response in [
            (['MANUAL', '80'], b'MANUAL 80\n', 'LOCAL command accepted=1\n' + control(1000) + '\n'),
            (['AUTO'], b'AUTO\n', 'LOCAL command accepted=1\n' + control(1000, mode='AUTO') + '\n'),
        ]:
            connection = Connection(response)
            fake = types.SimpleNamespace(serial_for_url=mock.Mock(return_value=connection), SerialException=OSError)
            with tempfile.TemporaryDirectory() as folder, mock.patch.object(CLIENT, 'EVIDENCE', Path(folder)):
                with mock.patch.dict('sys.modules', {'serial': fake}), redirect_stdout(io.StringIO()):
                    self.assertEqual(CLIENT.main(args), 0)
                self.assertEqual(connection.sent, expected)
                self.assertFalse(connection.dtr)
                self.assertFalse(connection.rts)
                saved = list(Path(folder).glob('*.log'))
                self.assertEqual(len(saved), 1)
                self.assertIn('RX CONTROL', saved[0].read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
