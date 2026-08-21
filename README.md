# nextnano.nvim

Syntax highlighting and keyword completion for nextnano++ input files (`.in`) in
Neovim.

Every documented group, attribute and built-in function is known to the plugin —
generated straight from the [nextnano++ documentation](https://www.nextnano.com/docu/nextnanoplus/latest/user_guide/keywords/)
by `tools/gen_keywords.py`. A keyword the docs do not know is highlighted as an
error, so a file that highlights clean is very nearly a file that parses.

## Features

- Filetype detection for `.in` files (Neovim's builtin rule leaves them unset)
- Scope-aware keywords: one syntax region per documented group, so
  `optics{ temperature = 300 }` is flagged even though `temperature` is a real
  keyword elsewhere
- Unknown groups, attributes and function calls highlighted as errors
- Integers, floats, `$variables`, `yes`/`no`, strings, `#` and `!TEXT` comments,
  `!IF` / `!ELIF` / `!ENDIF` and friends, operators, XML tags
- The 39 documented built-in functions (`sqrt`, `erfc`, `fdmhalf`, …); anything
  else before a `(` is flagged
- Omni completion (`<C-x><C-o>`) offering exactly the groups and attributes valid
  at the cursor. nvim-cmp and blink.cmp pick this up through their omnifunc
  sources
- Folding per group, `#` comment string for `gc`, bracket matching

## Install

**lazy.nvim**

```lua
{ "alikaansun/nextnano.nvim", ft = "nextnano" }
```

**Nix** — the repo is a package:

```nix
nextnanoPlugin = pkgs.callPackage /path/to/nextnano.nvim { };
```

**Manual**

```sh
git clone https://github.com/alikaansun/nextnano.nvim \
  ~/.local/share/nvim/site/pack/plugins/start/nextnano.nvim
```

> With `lazy = true` / `ft = "nextnano"`, `plugin/nextnano.lua` still runs at
> startup because lazy.nvim reads the plugin's filetype registration eagerly. If
> detection ever fails, add
> `vim.filetype.add({ extension = { ["in"] = "nextnano" } })` to your config.

## Options

```vim
let g:nextnano_highlight_unknown = 0
```

Stops unrecognised keywords from being highlighted as errors. Worth setting if
your nextnano version is ahead of the online documentation, or if you use
keywords it no longer documents (`output_wavefunctions`, say, which the docs now
call `output_states`).

## Colors

Everything links to standard highlight groups, so it follows your colorscheme:

| group | linked to | what |
|---|---|---|
| `nextnanoGroupName` | `Statement` | group names before `{` |
| `nextnanoAttribute` | `Keyword` | attribute names before `=` |
| `nextnanoNumber` | `Number` | integers |
| `nextnanoFloat` | `Constant` | floats — deliberately not `Number`, so the two differ |
| `nextnanoFunction` | `Function` | built-in functions |
| `nextnanoVariable` | `Identifier` | `$variables` |
| `nextnanoUnknown` | `Error` | undocumented keyword |

```lua
vim.api.nvim_set_hl(0, "nextnanoAttribute", { link = "Identifier" })
```

## Regenerating the keyword data

`syntax/nextnano_keywords.vim` and `lua/nextnano/keywords.lua` are generated and
committed. After a new nextnano release:

```sh
python3 tools/gen_keywords.py   # ~15 s, only needs the standard library
bash tools/test_syntax.sh       # asserts the highlighting on sample.in
```

The generator reads the documentation's Sphinx `searchindex.js` for the keyword
tree, then the keyword pages and tutorials for the attributes that are only ever
shown in tables and examples.
