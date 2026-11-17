"""Artifact routing checks use distinct dummy files, never claim a real firmware build."""
import configparser
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import tomllib
import unittest

SPEC = importlib.util.spec_from_file_location('prepare_simulation', Path(__file__).resolve().parents[2] / 'scripts/prepare-simulation.py')
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class PreparationChecks(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        (self.root / 'platformio.ini').write_text('fixture')
        os.utime(self.root / 'platformio.ini', (100, 100))
        for node, env in PREPARE.NODE_ENVIRONMENTS.items():
            for name in PREPARE.ARTIFACTS:
                p = self.root / '.pio/build' / env / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((node + name).encode())
                os.utime(p, (200, 200))

    def prepare(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return PREPARE.prepare(self.root, *args)

    def test_all_routes_distinct_artifacts_and_manifests(self):
        self.assertEqual(len(self.prepare('all')), 3)
        for node, env in PREPARE.NODE_ENVIRONMENTS.items():
            dest = self.root / 'simulations' / node / 'build'
            manifest = json.loads((dest / 'manifest.json').read_text())
            self.assertEqual(manifest['environment'], env)
            self.assertEqual(manifest['node_id'], node)
            for name in PREPARE.ARTIFACTS:
                self.assertEqual((dest / name).read_bytes(), (node + name).encode())
                self.assertEqual(manifest['artifacts'][name]['sha256'], PREPARE.digest(dest / name))

    def test_default_preserves_node_one_only(self):
        self.prepare()
        self.assertTrue((self.root / 'simulations/node_01/build/firmware.bin').exists())
        self.assertFalse((self.root / 'simulations/node_02').exists())

    def test_missing_selected_environment_does_not_fall_back(self):
        (self.root / '.pio/build/node_02/firmware.bin').unlink()
        with self.assertRaisesRegex(RuntimeError, 'node_02'):
            self.prepare('all')
        self.assertFalse((self.root / 'simulations').exists())

    def test_empty_artifact_is_rejected(self):
        (self.root / '.pio/build/node_03/firmware.elf').write_bytes(b'')
        with self.assertRaisesRegex(RuntimeError, 'empty'):
            self.prepare('node_03')

    def test_source_change_invalidates_old_artifacts(self):
        p = self.root / 'src/Identity.h'
        p.parent.mkdir()
        p.write_text('changed')
        os.utime(p, (300, 300))
        with self.assertRaisesRegex(RuntimeError, 'older'):
            self.prepare()

    def test_real_node_configs_match_mapping_and_hardware(self):
        root = Path(__file__).resolve().parents[2]
        config = configparser.ConfigParser()
        config.read(root / 'platformio.ini')
        self.assertEqual(config['platformio']['default_envs'], 'esp32dev')
        diagram = json.loads((root / 'simulations/node_01/diagram.json').read_text())
        self.assertEqual(next(p for p in diagram['parts'] if p['id'] == 'esp')['attrs']['cpuFrequency'], '4')
        for index, (node, env) in enumerate(PREPARE.NODE_ENVIRONMENTS.items(), 1):
            self.assertEqual(config[f'env:{env}']['build_flags'], f'-DSMARTLIGHT_NODE_INDEX={index}')
            self.assertEqual(json.loads((root / 'simulations' / node / 'diagram.json').read_text()), diagram)
            wokwi = tomllib.loads((root / 'simulations' / node / 'wokwi.toml').read_text())['wokwi']
            self.assertEqual(wokwi['rfc2217ServerPort'], 3999 + index)
            self.assertEqual(wokwi['firmware'], 'build/firmware.bin')
            self.assertEqual(wokwi['elf'], 'build/firmware.elf')

    def test_unknown_node_rejected(self):
        with self.assertRaises(ValueError):
            self.prepare('node_04')


if __name__ == '__main__':
    unittest.main()
