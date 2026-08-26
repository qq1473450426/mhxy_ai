import unittest

from engine.perception import PerceptionConfig, ScreenLevelingObserver


class PerceptionParserTests(unittest.TestCase):
    def test_parse_level(self):
        self.assertEqual(ScreenLevelingObserver._parse_level('等级：59'), 59)
        self.assertEqual(ScreenLevelingObserver._parse_level('LV 69'), 69)

    def test_parse_percent(self):
        self.assertEqual(ScreenLevelingObserver._parse_percent('经验 87%'), 87)
        self.assertIsNone(ScreenLevelingObserver._parse_percent('经验未知'))

    def test_ocr_candidates(self):
        observer = ScreenLevelingObserver(config=PerceptionConfig())
        candidates = observer._build_candidates({}, '请选择角色进入游戏')
        self.assertTrue(candidates)
        self.assertEqual(candidates[0].state, 'CHARACTER_SELECT')
        self.assertGreaterEqual(candidates[0].confidence, 0.72)

    def test_unknown_is_conservative(self):
        observer = ScreenLevelingObserver(config=PerceptionConfig())
        candidates = observer._build_candidates({}, '一段无法确定界面的文字')
        self.assertEqual(candidates, [])


if __name__ == '__main__':
    unittest.main()
