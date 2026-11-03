#!/usr/bin/env python3
"""Exercise Chinese and mounted Japanese input in real librime sessions.

Requires RIME_DEPLOYER, RIME_LUA_PLUGIN and RIME_LIBRARY. Optional
RIME_INCLUDE_DIR points to the directory containing rime_api.h.
"""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

from runtime import ROOT, prepare_runtime

DEPLOYER = os.environ.get("RIME_DEPLOYER")
LUA_PLUGIN = os.environ.get("RIME_LUA_PLUGIN")
RIME_LIBRARY = os.environ.get("RIME_LIBRARY")
INCLUDE_DIR = Path(os.environ.get("RIME_INCLUDE_DIR", "/usr/include"))


@unittest.skipUnless(
    DEPLOYER and LUA_PLUGIN and RIME_LIBRARY and INCLUDE_DIR.joinpath("rime_api.h").is_file(),
    "set RIME_DEPLOYER, RIME_LUA_PLUGIN, RIME_LIBRARY and optionally RIME_INCLUDE_DIR",
)
class MojiChineseLibrimeInputTest(unittest.TestCase):
    def test_chinese_and_mounted_japanese_input(self):
        with tempfile.TemporaryDirectory(prefix="moji-zh-lua-") as temp_dir:
            temp = Path(temp_dir)
            user, shared, stage = prepare_runtime(temp)
            env = os.environ.copy()

            subprocess.run(
                [DEPLOYER, "--build", str(user), str(shared), str(stage)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            compiled = yaml.safe_load(
                (stage / "moji_zh.schema.yaml").read_text(encoding="utf-8")
            )
            processors = compiled["engine"]["processors"]
            self.assertEqual(processors[0], "key_binder")
            self.assertLess(
                processors.index("lua_processor@*moji_zh/ja_speller"),
                processors.index("ascii_composer"),
            )
            self.assertNotIn("lua_filter@*moji_zh/candidate_order", compiled["engine"]["filters"])

            executable = temp / "librime_zh_input_test"
            subprocess.run(
                [
                    os.environ.get("CXX", "g++"),
                    "-std=c++17",
                    str(ROOT / "tests/moji_zh/librime_zh_input_test.cc"),
                    f"-I{INCLUDE_DIR}",
                    RIME_LIBRARY,
                    "-ldl",
                    "-Wl,--allow-shlib-undefined",
                    "-o",
                    str(executable),
                ],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            input_result = subprocess.run(
                [str(executable), LUA_PLUGIN, str(shared), str(user), str(stage)],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(
                input_result.returncode,
                0,
                input_result.stdout + input_result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
