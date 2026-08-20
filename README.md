# nextnano.nvim

Syntax highlighting for nextnano++ input files (`.in`) in Neovim.

A port of the [nextnano VSCode extension](https://github.com/alikaansun/nextnano-vscode-extension)'s
TextMate grammar to a Vim syntax file.

## Features

- Filetype detection for `.in` files (Neovim's builtin rule leaves them unset)
- Highlighting for comments, strings, `$variables`, integers, floats, `yes`/`no`,
  control keywords, and the nextnano++ section keywords (`global`, `structure`,
  `grid`, `quantum`, `poisson`, …)
- `#` comment string, so `gcc` / `gc` in comment plugins works out of the box
- Bracket matching for `()`, `{}`, `[]`

## Install

**lazy.nvim**

```lua
{ "alikaansun/nextnano.nvim", ft = "nextnano" }
```

**packer.nvim**

```lua
use { "alikaansun/nextnano.nvim" }
```

**Manual**

```sh
git clone https://github.com/alikaansun/nextnano.nvim \
  ~/.local/share/nvim/site/pack/plugins/start/nextnano.nvim
```

> With `lazy = true` / `ft = "nextnano"`, `plugin/nextnano.lua` still runs at
> startup because lazy.nvim reads the plugin's `ftdetect`/filetype registration
> eagerly. If detection ever fails, add
> `vim.filetype.add({ extension = { ["in"] = "nextnano" } })` to your config.

## Colors

Everything links to standard highlight groups (`Comment`, `String`, `Number`,
`Float`, `Boolean`, `Conditional`, `Identifier`, `Function`), so it picks up
whatever colorscheme you use. Override in your config if you want something
different:

```lua
vim.api.nvim_set_hl(0, "nextnanoSection", { link = "Keyword" })
```
