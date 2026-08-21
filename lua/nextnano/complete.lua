-- Omni completion for nextnano++ input files. The syntax file already nests one
-- region per documented group, so the enclosing group is whatever nnG_ item sits
-- on top of the syntax stack -- no second parser needed.

local kw = require("nextnano.keywords")

local M = {}

--- Dotted path of the innermost group at a position, "" at file scope.
function M.path_at(lnum, col)
  local stack = vim.fn.synstack(lnum, math.max(col, 1))
  for i = #stack, 1, -1 do
    local path = kw.groups[vim.fn.synIDattr(stack[i], "name")]
    if path then
      return path
    end
  end
  return ""
end

function M.omnifunc(findstart, base)
  local line = vim.fn.getline(".")
  local col = vim.fn.col(".") - 1
  if findstart == 1 then
    local start = col
    while start > 0 and line:sub(start, start):match("[%w_]") do
      start = start - 1
    end
    return start
  end

  local items = {}
  local path = M.path_at(vim.fn.line("."), col)

  -- Right of an "=", the useful candidates are that attribute's allowed values,
  -- not more keyword names. Attributes taking a number or an array have none,
  -- and then offering nothing is better than offering the wrong list.
  local attr = line:sub(1, col):match("([%a_][%w_]*)%s*=%s*[%w_]*$")
  if attr then
    local key = path == "" and attr or path .. "." .. attr
    for _, value in ipairs(kw.values[key] or {}) do
      if vim.startswith(value, base) then
        table.insert(items, { word = value, kind = "v", menu = "value" })
      end
    end
    return items
  end

  for _, entry in ipairs(kw.tree[path] or {}) do
    local word, kind = entry[1], entry[2]
    if vim.startswith(word, base) then
      table.insert(items, {
        word = word,
        kind = kind,
        menu = kind == "g" and "group" or "attribute",
      })
    end
  end
  return items
end

return M
