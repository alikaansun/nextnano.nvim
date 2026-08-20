-- Neovim's builtin rule for "*.in" strips the extension and detects on the
-- remaining name, which leaves a plain "sample.in" with no filetype at all.
vim.filetype.add({ extension = { ["in"] = "nextnano" } })
