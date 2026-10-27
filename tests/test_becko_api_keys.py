"""Config corruption, precedence, normalization and migration regressions."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import api_keys

class KeyLoadingTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config = Path(self.directory.name)/'keys.json'
        self.path_patch = patch.object(api_keys, 'CONFIG_PATH', self.config)
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)
        self.env_patch = patch.dict('os.environ', {}, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def test_env_priority_whitespace_and_dedup(self):
        self.config.write_text(json.dumps({'gemini_api_key':' disk ', 'gemini_api_keys':['env',' other ', None, 12]}))
        with patch.dict('os.environ', {'BECKO_GEMINI_API_KEY':' env ', 'BECKO_GEMINI_API_KEYS':'second, env, '}):
            self.assertEqual(api_keys.get_all_keys(), ['env', 'second', 'disk', 'other'])

    def test_legacy_environment_still_loads(self):
        with patch.dict('os.environ', {'KAIZUMI_GEMINI_API_KEY':'legacy'}):
            self.assertEqual(api_keys.get_all_keys(), ['legacy'])

    def test_malformed_config_does_not_hide_env(self):
        for value in ['[]', 'null', '42', '"text"', '{broken']:
            self.config.write_text(value)
            with patch.dict('os.environ', {'BECKO_GEMINI_API_KEY':'env'}):
                self.assertEqual(api_keys.get_all_keys(), ['env'])

    def test_missing_config_without_env_is_empty(self):
        self.assertEqual(api_keys.get_all_keys(), [])

    def test_explicit_config_path_matches_ui_readiness(self):
        other = self.config.with_name('ui.json')
        other.write_text('{"gemini_api_key":"ui-key"}')
        self.assertEqual(api_keys.get_all_keys(other), ['ui-key'])

    def test_add_key_still_updates_config(self):
        self.config.write_text('{}')
        self.assertEqual(api_keys.add_key('AIzaTestOnly'), 1)
        self.assertEqual(api_keys.get_all_keys(), ['AIzaTestOnly'])
