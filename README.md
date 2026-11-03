# rime-moji

[English](README.md) | [简体中文](README.zh-CN.md)

Rime input-method schemas for Japanese and Chinese. The project contains a
Kagiroi-derived Japanese romaji schema (`moji_ja`) and a pinyin-focused Chinese
schema (`moji_zh`) with Japanese input mounted under the `ja` prefix. Both
schemas use `librime-lua` for their Lua components.

## Schemas

### `moji_ja`

Japanese romaji-to-kana/kanji conversion, based on the pinned Kagiroi snapshot.
The active layout is romaji; auxiliary schemas and dictionaries provide the
kana/kanji, romaji, and part-of-speech connection data needed by the translator.

### `moji_zh`

A pinyin schema based on a reduced Rime-Ice configuration. It imports the 8105
character table and base dictionary, and can mount `moji_ja` when the input
starts with `ja`.

Important behavior and configuration decisions:

- The `zh_ja` / `zh_only` options default to `zh_ja`; `ascii_mode.reset` remains
  `1`. The `hiragana`, `katakana`, and `hw_katakana` switches are declared in
  this schema as well as in `moji_ja`, because dependent schemas do not inherit
  switch declarations.
- In mounted Japanese mode, **left Shift** is the ASCII escape. Right Shift
  keeps the normal `ascii_composer` behavior.
- `key_binder` is first in the Chinese processor chain, and the Japanese
  adapter runs before `ascii_composer`. Global `-` and `=` keys page candidates.
- Shared defaults provide email/URL/underscore recognizers, `F4` schema/options
  selection, `Tab`/`Shift+Tab` candidate cycling, and punctuation settings.
  `moji_ja` also retains `Ctrl+u/i/o` kana-mode shortcuts and its 3-dan
  punctuation table.
- `custom_phrase` remains disabled. It is not used as an unexamined substitute
  for candidate ordering or pinning behavior.
- English input, emoji, and simplified/traditional conversion are outside the
  current Chinese scope.

## Install and test

The optional `weasel.custom.yaml` and `squirrel.custom.yaml` files provide
client-specific overrides for Weasel (Windows) and Squirrel (macOS). Install
the applicable file alongside the shared Rime configuration before deploying;
these settings do not replace `default.custom.yaml`. They configure client
notifications, application-specific behavior, and candidate presentation.

Install the repository's schema, dictionary, Lua, and OpenCC files into the
shared Rime data directory, then deploy Rime. The Lua features require the
`librime-lua` plugin.

Static configuration checks:

```sh
python3 -m unittest discover -s tests/default.custom -v
python3 -m unittest discover -s tests/moji_ja -v
python3 -m unittest discover -s tests/moji_zh -v
```

The Japanese and Chinese suites also run real librime/librime-lua deployment
and input tests when `RIME_DEPLOYER`, `RIME_LUA_PLUGIN`, `RIME_LIBRARY`, and the
required include/library paths are available. See the test-directory README
files for environment setup. Integration tests use temporary data trees and
small fixtures; they do not alter the repository dictionaries or user data.

The runtime tests cover Japanese romaji conversion, pinyin candidate order and
commit, `-`/`=` paging, `ja`-prefix Japanese input, digit selection, continued
input after partial candidate selection, `zh_only`, and left/right Shift
behavior.

## Dictionary notes

- With `use_preset_vocabulary: false`, entries without an explicit weight have
  weight `0`; `sort: by_weight` does not generate weights.
- In Rime TSV dictionaries, the exact `# no comment` directive changes how
  subsequent `#`-prefixed lines are parsed. `#nocomment` is an ordinary
  comment, and blank lines are skipped.

## Intentional scope exclusions

These items were deliberately left out of the current migration; they are not
open implementation TODOs. Revisit them only after an explicit scope decision.

- `moji_zh` remains pinyin plus mounted Japanese input: English, emoji, and
  simplified/traditional conversion are not included. `custom_phrase` stays
  disabled, and the preliminary `candidate_order` filter and `ba:吧` rule were
  removed rather than shipped without a defined ordering policy.
- `moji_ja` uses the selected romaji layout only. Alternative layouts
  (`ansikana`, `szromaji`), emoji/reverse lookup, and optional `nico`,
  `kaomoji`, and symbols dictionaries were not migrated.
- Japanese dictionary/matrix generation inputs such as `kagiroi_id.def`,
  `lex_excluded.csv`, and `matrix_custom.def` are not distributed. Runtime
  conversion uses the already prepared data files.

## Open TODOs

- **Define special Chinese candidate pinning/override requirements.** Specify
  which codes and candidates are affected, expected ordering, and interaction
  with user dictionaries; add regression tests before considering an
  implementation. Until then, no pinning filter is enabled, and
  `custom_phrase` is not a substitute.
- **Decide whether Japanese manual phrases and gikun readings are needed.**
  They are not implemented. If approved, define a safe entry format, validate
  POS connection IDs, and add behavior tests before enabling a custom workflow.

Reproducible Japanese dictionary/matrix generation is optional follow-up work,
not a current TODO; it would require obtaining and pinning the build inputs
listed above.

## Maintenance

- `README.md` is the canonical English overview; keep `README.zh-CN.md` in sync
  when scope, behavior, setup, tests, or licensing guidance changes.
- Changes to switches, processor/segmentor order, key bindings, recognizer
  patterns, or mounted Japanese input must be reflected in the corresponding
  schema/component comments and `tests/default.custom`, `tests/moji_ja`, or
  `tests/moji_zh`. Preserve the documented `zh_ja` default, ASCII reset,
  left/right Shift distinction, and processor ordering unless intentionally
  changing them; update tests and both READMEs when doing so.
- Changes to dictionaries, Lua modules, generated tables, or OpenCC mappings
  require an updated source/modification/license header and an update to
  `THIRD_PARTY_NOTICES.md`. OpenCC JSON cannot safely carry comments, so record
  its provenance there. When changing an upstream snapshot, update the pinned
  commit, source mapping, license text if needed, and affected tests.
- Keep every YAML file comment-first and free of a UTF-8 BOM. Do not add the
  temporary `refs/` snapshots to project commits; cite the pinned upstream
  revision in the relevant header and third-party notice instead.
- Enabling `custom_phrase` requires an explicit schema and behavior review; do
  not assume it implements candidate ranking or pinning.

## AI usage

Development assistance used the **pi agent** as the harness and **gpt-6-luna**
as the LLM. Project maintainers remain responsible for reviewing changes.

## License and source data

Original project-authored material is MIT-licensed; see [LICENSE](LICENSE).
Third-party files retain their applicable licenses, identified in file headers
where comments are safe. The pinned upstream revisions, file mappings,
modifications, license texts, and nested-data attributions are documented in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [`LICENSES/`](LICENSES/).

**Chinese dictionary provenance note:** the pinned Rime-Ice repository declares
the resulting dictionary files GPL-3.0-only, and this project retains that
declaration and the upstream source credits. Its 8105 table also cites
Wiktionary-derived material (credited under CC BY-SA 4.0) and a BLCU frequency
table. Its base table lists Huayu, THUOCL, a modern-Chinese word-list Gist, and
Tencent AI Lab word vectors. Rime-Ice does not pin revisions for those external
source datasets, and the cited upstream snapshot does not state separate
redistribution terms for some of them. This project preserves the upstream
GPL declaration and source attributions; it does **not** claim an independent
license grant from any source whose terms are not stated. The detailed sources
and this limitation are recorded in the third-party notice.

## Upstream references

- [rime-kagiroi](https://github.com/rimeinn/rime-kagiroi/tree/808a195415e6d7bd3a41b1747039d8459bfde207): Japanese schema and data.
- [rime-ice](https://github.com/iDvel/rime-ice/tree/99662ba01e3affa6a0f009174ca530b887bac3b6): Chinese pinyin configuration and dictionaries.
- [rime-prelude](https://github.com/rime/home/tree/082425ea0684bca36474415d4a0e8db9b016487e/prelude): default configuration patterns.
- [rime-mkm](https://github.com/rimeinn/rime-mkm/tree/39bf741a70a5503e13ba1f84a6068c1b39c5f73d): mounted-prefix architecture reference.

Exact per-file provenance and license notices are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
