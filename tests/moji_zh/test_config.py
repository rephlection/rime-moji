#!/usr/bin/env python3
"""Fast static checks for the moji_zh component configuration."""

from pathlib import Path
import unittest

import yaml

from runtime import ROOT


class MojiChineseConfigTest(unittest.TestCase):
    def test_component_yaml_is_utf8_comment_first_and_valid(self):
        paths = [ROOT / "moji_zh.schema.yaml", *sorted((ROOT / "moji_zh").glob("*.yaml"))]
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_bytes()
                self.assertTrue(content.startswith(b"#"), "YAML must start with a comment")
                self.assertFalse(content.startswith(b"\xef\xbb\xbf"), "unexpected UTF-8 BOM")
                yaml.safe_load(content.decode("utf-8"))

    def test_engine_order_and_removed_candidate_filter(self):
        schema = yaml.safe_load((ROOT / "moji_zh.schema.yaml").read_text(encoding="utf-8"))
        processors = schema["engine"]["processors"]
        self.assertEqual(processors[0], "key_binder")
        self.assertLess(
            processors.index("lua_processor@*moji_zh/ja_speller"),
            processors.index("ascii_composer"),
        )
        self.assertEqual(schema["engine"]["filters"], ["uniquifier"])
        self.assertNotIn("candidate_order", schema)
        self.assertEqual(schema["key_binder"]["__include"], "moji_zh/processor.key_binder:/key_binder")
        switches = schema["switches"]
        ascii_mode = next(switch for switch in switches if switch.get("name") == "ascii_mode")
        self.assertEqual(ascii_mode["reset"], 1)
        option_groups = {tuple(switch["options"]): switch for switch in switches if "options" in switch}
        self.assertEqual(option_groups[("zh_ja", "zh_only")]["reset"], 0)
        self.assertIn(("hiragana", "katakana", "hw_katakana"), option_groups)


if __name__ == "__main__":
    unittest.main()
