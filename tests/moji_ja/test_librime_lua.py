#!/usr/bin/env python3
"""Exercise moji_ja kana input through the real librime-lua processor.

Requires RIME_DEPLOYER, RIME_LUA_PLUGIN and RIME_LIBRARY. Optional
RIME_INCLUDE_DIR points to the directory containing rime_api.h.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEPLOYER = os.environ.get("RIME_DEPLOYER")
LUA_PLUGIN = os.environ.get("RIME_LUA_PLUGIN")
RIME_LIBRARY = os.environ.get("RIME_LIBRARY")
INCLUDE_DIR = Path(os.environ.get("RIME_INCLUDE_DIR", "/usr/include"))


@unittest.skipUnless(
    DEPLOYER and LUA_PLUGIN and RIME_LIBRARY and INCLUDE_DIR.joinpath("rime_api.h").is_file(),
    "set RIME_DEPLOYER, RIME_LUA_PLUGIN, RIME_LIBRARY and optionally RIME_INCLUDE_DIR",
)
class LibrimeLuaInputTest(unittest.TestCase):
    def test_romaji_sequences_through_lua_processor(self):
        with tempfile.TemporaryDirectory(prefix="moji-ja-lua-") as temp_dir:
            temp = Path(temp_dir)
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
            shutil.copytree(ROOT / "lua/moji_ja", shared / "lua/moji_ja")
            shutil.copytree(ROOT / "opencc/moji_ja", shared / "opencc/moji_ja")
            shutil.copytree(ROOT / "dict/moji_ja", shared / "dict/moji_ja")

            # Keep the real small romaji dictionary; stub the large tables so
            # the test focuses on Lua key processing and deploys quickly.
            for table in ("mozc", "kanji", "matrix"):
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
                env=os.environ.copy(),
            )

            executable = temp / "librime_lua_input_test"
            compiler = os.environ.get("CXX", "g++")
            subprocess.run(
                [
                    compiler,
                    "-std=c++17",
                    str(ROOT / "tests/moji_ja/librime_lua_input_test.cc"),
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
            )
            input_result = subprocess.run(
                [
                    str(executable),
                    LUA_PLUGIN,
                    str(shared),
                    str(user),
                    str(stage),
                    "konnichiha",
                    "こんにちは",
                    "nn",
                    "ん",
                    "nni",
                    "んに",
                    "nnya",
                    "んにゃ",
                    "n'",
                    "ん",
                ],
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )
            self.assertEqual(
                input_result.returncode,
                0,
                input_result.stdout + input_result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
