"""Becko voice defaults and malformed preference regressions, offline."""
import unittest
from assistant_settings import DEFAULT_VOICE, normalize_voice, get_voice_from_memory

class VoiceSettingsTest(unittest.TestCase):
    def test_default_and_reset_use_male_voice(self):
        self.assertEqual(DEFAULT_VOICE, 'Charon')
        for value in ['default', 'auto', 'normal', 'standart', 'erkak', 'male']:
            with self.subTest(value=value):
                self.assertEqual(normalize_voice(value), 'Charon')

    def test_saved_explicit_choice_is_respected(self):
        self.assertEqual(get_voice_from_memory({'preferences': {'assistant_voice': {'value': 'Puck'}}}), 'Puck')
        self.assertEqual(get_voice_from_memory({'preferences': {'assistant_voice': 'Aoede'}}), 'Aoede')

    def test_corrupt_or_missing_preferences_fall_back(self):
        for value in [None, [], {}, {'preferences': None}, {'preferences': []},
                      {'preferences': 'broken'}, {'preferences': {'assistant_voice': {'value': 'invalid'}}}]:
            with self.subTest(value=value):
                self.assertEqual(get_voice_from_memory(value), 'Charon')

    def test_normalizes_catalog_names(self):
        self.assertEqual(normalize_voice('  fEnRiR '), 'Fenrir')
        self.assertEqual(normalize_voice('not-a-voice'), '')
