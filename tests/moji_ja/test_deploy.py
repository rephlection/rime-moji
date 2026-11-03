#!/usr/bin/env python3
"""Deploy a small fixture of the moji_ja schema with librime."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
DEPLOYER = os.environ.get("RIME_DEPLOYER")


@unittest.skipUnless(DEPLOYER, "set RIME_DEPLOYER to run the librime integration test")
class MojiJapaneseDeployTest(unittest.TestCase):
    def test_schema_and_dependencies_deploy(self):
        with tempfile.TemporaryDirectory(prefix="moji-ja-deploy-") as temp:
            temp = Path(temp)
            user, shared, stage = (temp / name for name in ("user", "shared", "stage"))
            for directory in (user, shared, stage):
                directory.mkdir()

            for filename in ("default.yaml", "key_bindings.yaml", "punctuation.yaml"):
                shutil.copy2(ROOT / "refs/rime-prelude" / filename, shared)
            for path in ROOT.glob("moji_ja*.schema.yaml"):
                shutil.copy2(path, shared)
            for path in ROOT.glob("moji_ja*.dict.yaml"):
                shutil.copy2(path, shared)
            shutil.copytree(ROOT / "moji_ja", shared / "moji_ja")
            (shared / "opencc").mkdir()
            shutil.copytree(ROOT / "opencc/moji_ja", shared / "opencc/moji_ja")
            (shared / "dict").mkdir()
            shutil.copytree(ROOT / "dict/moji_ja", shared / "dict/moji_ja")

            # Tiny valid tables keep this config smoke test fast; production-sized
            # dictionaries are verified separately by the source migration checks.
            for table in ("mozc", "romaji", "kanji", "matrix"):
                table_id = f"dict/moji_ja/{table}"
                (shared / f"{table_id}.dict.yaml").write_text(
                    "# Test table\n"
                    "---\n"
                    f"name: {table_id}\n"
                    "version: '1'\n"
                    "sort: by_weight\n"
                    "use_preset_vocabulary: false\n"
                    "...\n"
                    "あ\ta\t1\n",
                    encoding="utf-8",
                )
            (user / "default.custom.yaml").write_text(
                "# Test schema list\n"
                "patch:\n"
                "  schema_list:\n"
                "    - schema: moji_ja\n",
                encoding="utf-8",
            )

            subprocess.run(
                [DEPLOYER, "--build", str(user), str(shared), str(stage)],
                check=True,
                capture_output=True,
                text=True,
            )
            schema = yaml.safe_load((stage / "moji_ja.schema.yaml").read_text(encoding="utf-8"))
            self.assertEqual(schema["schema"]["schema_id"], "moji_ja")
            self.assertEqual(
                schema["schema"]["dependencies"],
                ["moji_ja.aux.romaji", "moji_ja.aux.kanji", "moji_ja.aux.matrix"],
            )
            self.assertIn("recognizer", schema["engine"]["processors"])
            self.assertNotIn("import_preset", schema["recognizer"])
            patterns = schema["recognizer"]["patterns"]
            self.assertTrue({"email", "uppercase", "url"}.issubset(patterns))
            self.assertEqual(schema["switches"][0]["name"], "ascii_mode")
            self.assertEqual(schema["switches"][0]["reset"], 1)
            self.assertEqual(schema["switches"][1]["options"], ["hiragana", "katakana", "hw_katakana"])
            self.assertEqual(schema["switches"][1]["reset"], 0)
            switch_names = [switch.get("name") for switch in schema["switches"]]
            self.assertNotIn("full_shape", switch_names)
            self.assertNotIn("ascii_punct", switch_names)
            bindings = schema["key_binder"]["bindings"]
            self.assertTrue(any(binding.get("accept") == "Control+u" for binding in bindings))
            punctuator = schema["punctuator"]
            self.assertIn("full_shape", punctuator)
            self.assertIn("half_shape", punctuator)
            self.assertIn("matcher", schema["engine"]["segmentors"])
            self.assertTrue((stage / "moji_ja.aux.romaji.schema.yaml").is_file())
            self.assertTrue((stage / "moji_ja.aux.kanji.schema.yaml").is_file())
            self.assertTrue((stage / "moji_ja.aux.matrix.schema.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
