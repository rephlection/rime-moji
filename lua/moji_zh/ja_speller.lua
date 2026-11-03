-- SPDX-License-Identifier: GPL-3.0-only
-- SPDX-FileCopyrightText: 2026 rime-moji authors
-- Source: original rime-moji adapter; mounted-prefix design references
-- rimeinn/rime-mkm@39bf741a70a5503e13ba1f84a6068c1b39c5f73d.
-- Modifications: gates kana_speller on the Japanese option and ja prefix;
-- handles left-Shift ASCII escape, Enter, Escape, and kana-safe caret movement.
local japanese = require("moji_ja/kana_speller")
local M = {}

local function commit_reading(env)
    local ctx = env.engine.context
    -- script text retains the affix prefix; an empty ja can display as "j a".
    local text = ctx.input == env.prefix and "" or ctx:get_script_text()
    if text:sub(1, #env.prefix) == env.prefix then
        text = text:sub(#env.prefix + 1)
    end
    env.pending_n_input = nil
    if text ~= "" then
        env.engine:commit_text(text)
    end
    ctx:clear()
end

function M.init(env)
    japanese.init(env)
    env.prefix = env.engine.schema.config:get_string("moji_ja/prefix") or "ja"
end

function M.func(key, env)
    local ctx = env.engine.context
    local is_ascii_escape_shift = key.keycode == 0xffe1 -- Shift_L only
    if not is_ascii_escape_shift or key:ctrl() or key:alt() or key:super() then
        env.shift_tap = nil -- A chord is not a standalone Shift tap.
    end
    if not ctx:get_option("zh_ja") or ctx:get_option("ascii_mode")
        or ctx.input:sub(1, #env.prefix) ~= env.prefix then
        env.pending_n_input = nil
        env.shift_tap = nil
        return 2 -- kNoop; ordinary Chinese input is never converted.
    end
    -- Run before ascii_composer and consume Shift_L's press/release for this
    -- gesture. At bare `ja`, it clears the affix and switches to ASCII, so the
    -- following letters pass through as English instead of being romanized.
    -- Shift_R is deliberately left to ascii_composer; any intervening key
    -- cancels this tap gesture.
    if is_ascii_escape_shift and not key:ctrl() and not key:alt()
        and not key:super() then
        env.pending_n_input = nil
        if not key:release() then
            env.shift_tap = env.shift_tap or key.keycode
            return 1
        end
        local tap = env.shift_tap
        env.shift_tap = nil
        if not tap then
            return 2
        end
        if tap == key.keycode then
            commit_reading(env)
            ctx:set_option("ascii_mode", true)
        end
        return 1
    end
    -- Plain Enter commits the same reading, without switching to ASCII.
    if key.keycode == 0xff0d and not key:release() and not key:ctrl()
        and not key:alt() and not key:super() and not key:shift() then
        commit_reading(env)
        return 1 -- kAccepted; an empty prefix is simply dismissed.
    end
    -- A native affix composition can otherwise leave its prefix after Esc.
    -- Cancel the entire mounted input, not just the current Japanese segment.
    if key.keycode == 0xff1b and not key:release() and not key:ctrl()
        and not key:alt() and not key:super() then
        env.pending_n_input = nil
        ctx:clear()
        return 1 -- kAccepted
    end
    -- The Chinese navigator otherwise moves by affix segments/bytes. Keep plain
    -- arrows on kana boundaries inside the code segment, never inside UTF-8.
    if (key.keycode == 0xff51 or key.keycode == 0xff53) and not key:release()
        and not key:ctrl() and not key:alt() and not key:super() and not key:shift() then
        env.pending_n_input = nil
        local start = utf8.offset(ctx.input, 0, ctx.caret_pos + 1)
        local target
        if key.keycode == 0xff51 then
            target = (utf8.offset(ctx.input, -1, start) or 1) - 1
        else
            target = (utf8.offset(ctx.input, 2, start) or (#ctx.input + 1)) - 1
        end
        ctx.caret_pos = math.max(#env.prefix, target)
        return 1
    end
    return japanese.func(key, env)
end

function M.fini(env)
    japanese.fini(env)
end

return M
