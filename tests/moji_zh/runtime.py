"""Build a small isolated data tree for moji_zh librime integration tests."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def _write_dict(path: Path, name: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Test fixture dictionary\n"
        "---\n"
        f"name: {name}\n"
        "version: '1'\n"
        "sort: by_weight\n"
        "use_preset_vocabulary: false\n"
        "...\n"
        + "\n".join(rows)
        + "\n",
        encoding="utf-8",
    )


def prepare_runtime(temp: Path) -> tuple[Path, Path, Path]:
    user, shared, stage = (temp / part for part in ("user", "shared", "stage"))
    for directory in (user, shared, stage):
        directory.mkdir(parents=True)

    for filename in ("default.yaml", "key_bindings.yaml", "punctuation.yaml"):
        shutil.copy2(ROOT / "refs/rime-prelude" / filename, shared)
    for path in ROOT.glob("moji_*.schema.yaml"):
        shutil.copy2(path, shared)
    for path in ROOT.glob("moji_*.dict.yaml"):
        shutil.copy2(path, shared)

    for parent in (shared / "dict", shared / "lua", shared / "opencc"):
        parent.mkdir()
    for directory in ("moji_ja", "moji_zh"):
        shutil.copytree(ROOT / directory, shared / directory)
        shutil.copytree(ROOT / "dict" / directory, shared / "dict" / directory)
        shutil.copytree(ROOT / "lua" / directory, shared / "lua" / directory)
    shutil.copytree(ROOT / "opencc/moji_ja", shared / "opencc/moji_ja")
    shutil.copy2(ROOT / "default.custom.yaml", user / "default.custom.yaml")
    shutil.copytree(ROOT / "default.custom", user / "default.custom")

    # Tiny Chinese fixture with enough candidates to exercise ordering, selection,
    # and multiple pages.  Keep source frequencies in descending order.
    _write_dict(
        shared / "dict/moji_zh/8105.dict.yaml",
        "dict/moji_zh/8105",
        [
            "把\tba\t1000",
            "吧\tba\t900",
            "八\tba\t800",
            "爸\tba\t700",
            "巴\tba\t600",
            "罢\tba\t500",
            "拔\tba\t400",
        ],
    )
    _write_dict(shared / "dict/moji_zh/base.dict.yaml", "dict/moji_zh/base", [])

    # Tiny tables use the production entry and matrix formats. The distinct
    # あ / あい readings exercise Viterbi prefix candidates without full data.
    _write_dict(
        shared / "dict/moji_ja/mozc.dict.yaml",
        "dict/moji_ja/mozc",
        [
            "亜|1 1\tあ\t1000",
            "あ|1 1\tあ\t900",
            "愛|1 1\tい\t1000",
            "藍|1 1\tあい\t900",
        ],
    )
    _write_dict(
        shared / "dict/moji_ja/romaji.dict.yaml",
        "dict/moji_ja/romaji",
        ["あ\ta\t1", "い\ti\t1", "あい\tai\t1"],
    )
    _write_dict(
        shared / "dict/moji_ja/kanji.dict.yaml",
        "dict/moji_ja/kanji",
        ["亜|1 1\tあ\t10", "愛|1 1\tい\t10"],
    )
    _write_dict(
        shared / "dict/moji_ja/matrix.dict.yaml",
        "dict/moji_ja/matrix",
        [
            "0 0\t0",
            "0 1\t0",
            "1 0\t0",
            "1 1\t0",
            "-10 0\t0",
            "-10 1\t0",
            "0 -20\t0",
            "1 -20\t0",
        ],
    )

    return user, shared, stage
