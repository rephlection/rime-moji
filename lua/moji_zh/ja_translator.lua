-- SPDX-License-Identifier: GPL-3.0-only
-- SPDX-FileCopyrightText: 2026 rime-moji authors
-- Source: original rime-moji adapter; delegates to lua/moji_ja/translator.lua.
-- Modifications: gates translation by option and segment tag, preserving
-- original Phrase/Memory candidates and their learning behavior.
local japanese = require("moji_ja/translator")
local M = {}

function M.init(env)
    japanese.init(env)
end

function M.func(input, seg, env)
    if not env.engine.context:get_option("zh_ja") or not seg:has_tag("moji_ja") then
        return
    end
    -- Affix/caret recomposition can briefly expose a slice ending inside UTF-8.
    -- Do not cache that slice in Viterbi; the kana notifier repairs the caret.
    if not utf8.len(input) then
        return
    end
    japanese.func(input, seg, env)
end

function M.fini(env)
    japanese.fini(env)
end

return M
