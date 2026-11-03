#!/usr/bin/env python3
"""Integration smoke test using the real librime deployer, when available.

Run with RIME_DEPLOYER=/path/to/rime_deployer and its runtime libraries on
LD_LIBRARY_PATH.
"""

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
class LibrimeDefaultCustomTest(unittest.TestCase):
    def test_deployer_resolves_custom_component_includes(self):
        with tempfile.TemporaryDirectory(prefix="rime-default-custom-") as temp:
            temp = Path(temp)
            user = temp / "user"
            shared = temp / "shared"
            stage = temp / "stage"
            user.mkdir()
            shared.mkdir()
            stage.mkdir()

            shutil.copy2(ROOT / "default.custom.yaml", user)
            shutil.copytree(ROOT / "default.custom", user / "default.custom")
            for filename in ("default.yaml", "key_bindings.yaml", "punctuation.yaml"):
                shutil.copy2(ROOT / "refs" / "rime-prelude" / filename, shared)

            for schema_id in ("moji_zh", "moji_ja"):
                schema = shared / f"{schema_id}.schema.yaml"
                schema.write_text(
                    "# Minimal test schema\n"
                    "schema:\n"
                    f"  schema_id: {schema_id}\n"
                    "  name: Test\n"
                    "  version: '1.0'\n"
                    "engine:\n"
                    "  processors: [ascii_composer, recognizer, key_binder, punctuator, selector]\n"
                    "  segmentors: [abc]\n"
                    "  translators: [table_translator]\n"
                    "  filters: []\n",
                    encoding="utf-8",
                )

            subprocess.run(
                [DEPLOYER, "--build", str(user), str(shared), str(stage)],
                check=True,
                capture_output=True,
                text=True,
            )
            compiled = yaml.safe_load((stage / "default.yaml").read_text(encoding="utf-8"))

            self.assertEqual(compiled["ascii_composer"]["switch_key"]["Shift_L"], "commit_code")
            self.assertIn("underscore", compiled["recognizer"]["patterns"])
            self.assertIn("full_shape", compiled["punctuator"])
            self.assertIn("half_shape", compiled["punctuator"])
            bindings = compiled["key_binder"]["bindings"]
            self.assertIsInstance(bindings, list)
            self.assertTrue(any(item.get("accept") == "bracketleft" for item in bindings))
            self.assertTrue(any(item.get("accept") == "F4" for item in bindings))
            selector = compiled["selector"]
            for path in (
                ("bindings",),
                ("linear", "bindings"),
                ("vertical", "bindings"),
                ("vertical", "linear", "bindings"),
            ):
                node = selector
                for part in path:
                    node = node[part]
                self.assertEqual(node["Tab"], "next_candidate")
                self.assertEqual(node["ISO_Left_Tab"], "previous_candidate")


if __name__ == "__main__":
    unittest.main()
