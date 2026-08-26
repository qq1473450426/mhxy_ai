import unittest

from engine.perception import ScreenLevelingObserver


class PerceptionParserTests(unittest.TestCase):
    def test_parse_level(self):
        self.assertEqual(ScreenLevelingObserver._parse_level('等级：59'), 59)
        self.assertEqual(ScreenLevelingObserver._parse_level('LV 69'), 69)

    def test_parse_percent(self):
        self.assertEqual(ScreenLevelingObserver._parse_percent('经验 87%'), 87)
        self.assertIsNone(ScreenLevelingObserver._parse_percent('经验未知'))


if __name__ == '__main__':
    unittest.main()
