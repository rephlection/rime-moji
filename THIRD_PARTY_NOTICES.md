# Third-party notices and attribution

This is the consolidated notice for third-party material and source data in
this repository (including the attribution summary otherwise commonly placed
in a `NOTICE` file). Source revisions for repository snapshots are pinned
below. Original project-authored material is licensed under the root `LICENSE`
(MIT). A file-level SPDX identifier takes precedence for that file. No
third-party license is replaced or relicensed by the root license. This notice
also records source datasets whose upstream snapshot does not state separate
redistribution terms; those entries are provenance disclosures, not new grants
from their original publishers.

## rime-kagiroi — GPL-3.0-only

Source snapshot: [`rimeinn/rime-kagiroi` at
`808a195415e6d7bd3a41b1747039d8459bfde207`](https://github.com/rimeinn/rime-kagiroi/tree/808a195415e6d7bd3a41b1747039d8459bfde207).
The repository declares GPLv3. The following files are relocated or adapted
from it. Lua and YAML headers describe the local changes; OpenCC files are
listed here because JSON/text data are not annotated with inline comments:

- `lua/moji_ja/common.lua`, `kana_speller.lua`, `translator.lua`, and
  `viterbi.lua`;
- `moji_ja.schema.yaml`, `moji_ja.dict.yaml`, and the `moji_ja/` component
  configuration files;
- the Japanese OpenCC configuration and mapping files
  `opencc/moji_ja/h2k.json`, `h2k.txt`, `h2kh.json`, and `k2kh.txt` (renamed
  into the project namespace).

`lua/moji_ja/priority_queue.lua` is an exception: it retains its own zlib
license and full upstream notice. `lua/moji_ja/lru.lua` is MIT-licensed and
retains Boris Nagaev's copyright. The romaji table's upstream header declares
it public domain; this project records that declaration as
`LicenseRef-Public-Domain` and does not convert it to CC0.

### Nested Mozc material in Japanese data

Kagiroi documents use of Mozc dictionary and connection-matrix data and points
to Google Mozc revision
[`006ed69bf545548a8a3596b13f58cb22cf3d8a2f`](https://github.com/google/mozc/tree/006ed69bf545548a8a3596b13f58cb22cf3d8a2f).
The Mozc `dictionary_oss/README.txt` identifies IPADIC 2.7.0 and Okinawa
Dictionary material in the open-source dictionary. The IPADIC/ICOT notice and
Okinawa public-domain statement are included in `LICENSES/`. The Kagiroi-derived
`dict/moji_ja/mozc.dict.yaml` retains the Kagiroi GPL grant and the IPADIC
notice; the matrix is marked with the Kagiroi GPL grant because its upstream
source identifies Mozc connection data but does not state a separate nested
license for that matrix. The source README describes Okinawa Dictionary data as
public domain.

`dict/moji_ja/kanji.dict.yaml` carries the source file's BSD-3-Clause
identifier and Google copyright notice. `lua/moji_ja/segmenter.lua` is the
Kagiroi-generated module based on Mozc `src/data/rules/segmenter.def`. Its
header carries both the Kagiroi GPL-3.0-only grant for the generated module and
the Mozc BSD-3-Clause terms for the generated rules.

## rime-ice — GPL-3.0-only

Source snapshot: [`iDvel/rime-ice` at
`99662ba01e3affa6a0f009174ca530b887bac3b6`](https://github.com/iDvel/rime-ice/tree/99662ba01e3affa6a0f009174ca530b887bac3b6).
The upstream repository declares GPL-3.0-only. The following files are
adapted from the pinned snapshot:

- `dict/moji_zh/8105.dict.yaml`, `dict/moji_zh/base.dict.yaml`, and
  `moji_zh.dict.yaml`;
- `moji_zh.schema.yaml` and the `moji_zh/` processor/translator settings,
  except `moji_zh/segmentor.japanese.yaml`, which is project-authored under MIT.

The 8105 table's upstream header attributes character/pronunciation data to
Wiktionary contributors' [general-standard-character table](https://zh.wiktionary.org/wiki/Appendix:%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3%E7%B4%A2%E5%BC%95/%E9%80%9A%E7%94%A8%E8%A7%84%E8%8C%83%E6%B1%89%E5%AD%97%E8%A1%A8)
and frequencies to the BLCU 25-billion-character frequency table. The file
retains those attributions. Wiktionary content is published under CC BY-SA
4.0; the applicable license text is included in
`LICENSES/CC-BY-SA-4.0.txt`. The pinned rime-ice file cites mutable Wiktionary
and BLCU URLs rather than source revision IDs, so those data snapshots are
anchored to the rime-ice commit, not independently pinned. The cited BLCU page
does not state a separate data license in the source material reviewed here.
The compiled table retains the upstream GPL-3.0-only declaration; the
Wiktionary-derived material is additionally attributed and covered by the
CC-BY-SA-4.0 notice stated above.

The base table's upstream header lists the Huayu system lexicon, THUOCL,
`现代汉语常用词表`, and Tencent AI Lab word vectors, and also names dictionary
references. THUOCL is MIT-licensed; its copyright and permission notice are
included in `LICENSES/MIT.txt`. Its license was checked at
[`thunlp/THUOCL` revision `a30ce79d895d01ab5132a5c74c29703ff7efb4cc`](https://github.com/thunlp/THUOCL/tree/a30ce79d895d01ab5132a5c74c29703ff7efb4cc).
The other cited sources do not state separate redistribution terms in the
rime-ice snapshot, which does not pin revisions of those external datasets.
The base table is retained under the upstream rime-ice GPL-3.0-only
declaration, and all source credits from its upstream header are
preserved. This notice records the upstream grant and source disclosures; it
does not assert that the listed source datasets have independent licenses not
stated by their publishers.

## rime-prelude — LGPL-3.0-only

Source snapshot: [`rime/home` prelude at
`082425ea0684bca36474415d4a0e8db9b016487e`](https://github.com/rime/home/tree/082425ea0684bca36474415d4a0e8db9b016487e/prelude).
The upstream prelude is LGPL version 3. Its `AUTHORS` file names Gong Chen
for `default.yaml`; no individual author attribution is listed there for the
key-binding or punctuation files. The following custom configuration files
adapt those defaults and retain the LGPL-3.0-only notice:

- `default.custom.yaml`;
- `default.custom/processor/*.yaml`.

The local additions and deviations are summarized in each file header. The
source prelude `AUTHORS` file is available at the pinned upstream revision.
The [official Rime customization guide](https://github.com/rime/home/wiki/CustomizationGuide)
was also consulted for `__include`, `__patch`, and `__append` usage; it is a
documentation reference, not vendored content.

## Other direct dependencies and references

- `lua/moji_ja/lru.lua`: MIT, Copyright (c) 2015 Boris Nagaev; source is the
  copy carried by the pinned rime-kagiroi snapshot. The MIT notice is in
  `LICENSES/MIT.txt`.
- `lua/moji_ja/priority_queue.lua`: zlib, Copyright (C) 2017 Lucas de Morais
  Siqueira; the full notice remains in the file and is also in
  `LICENSES/Zlib.txt`.
- rime-mkm at
  [`39bf741a70a5503e13ba1f84a6068c1b39c5f73d`](https://github.com/rimeinn/rime-mkm/tree/39bf741a70a5503e13ba1f84a6068c1b39c5f73d)
  is cited as an architectural reference for prefix-mounted input. No source
  file from that repository is vendored as a dependency.
- librime and librime-lua were used as API/runtime references for tests; their
  implementation sources are not included in this project.

## License texts

Applicable license texts and the custom IPADIC/Okinawa source notices are in
`LICENSES/`. Project-created files use MIT where their file headers do not
identify an upstream license. Mixed-source data files retain their upstream
license and all identified nested notices rather than being relicensed under
MIT.
