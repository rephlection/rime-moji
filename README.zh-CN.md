# rime-moji

[English](README.md) | [简体中文](README.zh-CN.md)

面向 Rime 的日文和中文输入方案配置。本项目包含基于 Kagiroi 的日文罗马字方案 `moji_ja`，以及以拼音为范围的中文方案 `moji_zh`；中文方案通过 `ja` 前缀挂载日文输入。两个方案的 Lua 组件均依赖 `librime-lua`。

## 输入方案

### `moji_ja`

基于固定版本 Kagiroi 的日文罗马字到假名/汉字转换。当前启用罗马字布局；辅助 schema 和词典提供 translator 所需的假名/汉字、罗马字及词性连接数据。

### `moji_zh`

基于精简版 Rime-Ice 配置的拼音方案，导入 8105 字表和基础词库。输入以 `ja` 开头时可挂载 `moji_ja`。

重要行为和配置约定：

- `zh_ja` / `zh_only` 选项默认是 `zh_ja`；保留 `ascii_mode.reset: 1`。`hiragana`、`katakana`、`hw_katakana` switches 也在此 schema 中声明，因为依赖 schema 不会继承 switch 声明。
- 挂载日文输入时，**左 Shift** 用于退出日文前缀并切换 ASCII；右 Shift 保留 `ascii_composer` 原有行为。
- 中文 processor 链中 `key_binder` 必须在首位，日文 adapter 位于 `ascii_composer` 之前。全局使用 `-`、`=` 翻页。
- 全局默认配置提供邮箱/URL/下划线识别、`F4` 方案/选项切换、`Tab`/`Shift+Tab` 候选循环及标点配置。`moji_ja` 还保留 `Ctrl+u/i/o` 假名模式快捷键和 3-dan 标点表。
- `custom_phrase` 保持禁用；不把它未经审查地当作候选排序或置顶功能的替代品。
- 英文输入、emoji 和简繁转换不属于当前中文方案范围。

## 安装与测试

可选的 `weasel.custom.yaml` 和 `squirrel.custom.yaml` 分别提供 Weasel
（Windows）和 Squirrel（macOS）的客户端专属覆盖配置。将对应文件与 Rime
共享配置放在一起后再部署；这些配置不会替代 `default.custom.yaml`。它们设置客户端通知、特定应用行为及候选显示方式。

将项目中的 schema、词典、Lua 和 OpenCC 文件放入 Rime shared data 目录，然后部署 Rime。Lua 功能需要安装 `librime-lua` 插件。

配置结构检查：

```sh
python3 -m unittest discover -s tests/default.custom -v
python3 -m unittest discover -s tests/moji_ja -v
python3 -m unittest discover -s tests/moji_zh -v
```

如果配置了 `RIME_DEPLOYER`、`RIME_LUA_PLUGIN`、`RIME_LIBRARY` 以及所需的 include/library 路径，日文和中文测试还会执行真实 librime/librime-lua 部署与输入测试。环境设置见各测试目录中的 README。集成测试使用临时数据目录和小型 fixture，不会改写仓库词典或用户数据。

运行时测试覆盖日文罗马字转换、拼音候选顺序与提交、`-`/`=` 翻页、`ja` 前缀日文输入、数字选词、部分选词后继续输入、`zh_only` 及左右 Shift 行为。

## 词典说明

- `use_preset_vocabulary: false` 时，没有显式权重的词条权重为 `0`；`sort: by_weight` 不会自动生成权重。
- Rime TSV 词典中的精确指令 `# no comment` 会改变后续 `#` 开头行的解析方式。`#nocomment` 是普通注释，空行会被跳过。

## 明确排除的范围

以下功能是本次迁移时有意未纳入的，不是当前待实现的 TODO；只有明确调整范围后才重新评估。

- `moji_zh` 当前仅限拼音与挂载日文输入，不包含英文、emoji 和简繁转换。`custom_phrase` 保持禁用；由于候选排序规则尚未定义，预备的 `candidate_order` filter 和 `ba:吧` 规则已移除，而不是作为未审查功能发布。
- `moji_ja` 当前只采用选定的罗马字布局。备用布局（`ansikana`、`szromaji`）、emoji/反查及可选的 `nico`、`kaomoji` 和符号词库均未迁入。
- `kagiroi_id.def`、`lex_excluded.csv`、`matrix_custom.def` 等日文词典/矩阵生成输入不随项目分发；运行时转换使用已经准备好的数据文件。

## 当前 TODO

- **定义中文特殊候选置顶/覆盖规则。**明确影响哪些输入码和候选、排序预期以及与用户词典的交互，再补回归测试并评估实现。在规则确定前，不启用置顶 filter，也不把 `custom_phrase` 当作替代方案。
- **决定是否需要日文手工词条和 gikun 读音。**当前未实现；如确认需要，应先定义安全的词条格式、校验 POS 连接 ID，并补充行为测试，再启用相应流程。

可复现地生成日文词典/矩阵属于可选的后续维护工作，不是当前 TODO；若将来决定支持，需要先取得并固定上述构建输入。

## 维护约定

- `README.md` 是英文主文档；范围、行为、安装、测试或许可说明发生变化时，同步更新本文件。
- 修改 switches、processor/segmentor 顺序、按键绑定、recognizer 规则或日文挂载行为时，同步检查相应 schema/组件注释及 `tests/default.custom`、`tests/moji_ja`、`tests/moji_zh`。除非有意变更，否则保持文档所述的 `zh_ja` 默认值、ASCII reset、左右 Shift 区别和 processor 顺序；若变更，更新测试及两份 README。
- 修改词典、Lua 模块、生成表或 OpenCC 映射时，更新文件头中的来源/修改/许可说明及 `THIRD_PARTY_NOTICES.md`。OpenCC JSON 不适合安全地加注释，应在第三方声明中记录来源。升级上游快照时，同步更新固定 commit、文件映射、必要的许可文本及相关测试。
- 每个 YAML 文件都必须以注释开头且不得带 UTF-8 BOM。临时 `refs/` 快照不得提交；应在文件头和第三方声明中引用固定的上游版本。
- 启用 `custom_phrase` 前，应明确审查 schema 和实际行为；不要假设它实现了候选排序或置顶。

## AI 使用说明

开发过程中使用 **pi agent** 作为 harness，使用 **gpt-6-luna** 作为 LLM 提供辅助；项目维护者仍负责审查改动。

## 许可与数据来源

项目原创内容采用 MIT 许可，详见 [LICENSE](LICENSE)。第三方文件保留各自适用的许可；可安全添加注释的文件在头部注明许可。固定上游版本、文件映射、修改范围、许可文本和嵌套数据归属见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 与 [`LICENSES/`](LICENSES/)。

**中文词典来源说明：**固定版本的 Rime-Ice 仓库声明其整理后的词典文件采用 GPL-3.0-only，本项目保留该声明和上游来源标注。8105 字表还注明使用了 Wiktionary 来源数据（按 CC BY-SA 4.0 进行归属说明）和北语字频表；基础词库列出华宇词库、THUOCL、现代汉语词表 Gist 及腾讯 AI Lab 词向量。Rime-Ice 没有固定这些外部数据集的版本；所引用的上游快照也没有为其中部分来源说明独立的再分发许可。本项目保留 Rime-Ice 对合并词典的 GPL 声明和原有来源标注，**不声称任何未明确声明许可的来源另行授予了许可**。具体来源及限制见第三方声明文件。

## 上游参考

- [rime-kagiroi](https://github.com/rimeinn/rime-kagiroi/tree/808a195415e6d7bd3a41b1747039d8459bfde207)：日文 schema 和数据。
- [rime-ice](https://github.com/iDvel/rime-ice/tree/99662ba01e3affa6a0f009174ca530b887bac3b6)：中文拼音配置和词典。
- [rime-prelude](https://github.com/rime/home/tree/082425ea0684bca36474415d4a0e8db9b016487e/prelude)：默认配置组织方式参考。
- [rime-mkm](https://github.com/rimeinn/rime-mkm/tree/39bf741a70a5503e13ba1f84a6068c1b39c5f73d)：前缀挂载架构参考。

逐文件来源和许可证说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
