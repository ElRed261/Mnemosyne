vim.g.mapleader = " "

vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.mouse = "a"
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.termguicolors = true
vim.opt.signcolumn = "yes"
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.updatetime = 300

vim.keymap.set("n", "<leader>w", "<cmd>write<cr>", { desc = "Guardar" })
vim.keymap.set("n", "<leader>q", "<cmd>quit<cr>", { desc = "Salir" })
vim.keymap.set("n", "<leader>e", "<cmd>Explore<cr>", { desc = "Explorar archivos" })
vim.keymap.set("n", "<Esc>", "<cmd>nohlsearch<cr>")

vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function()
    vim.highlight.on_yank({ timeout = 150 })
  end,
})

vim.api.nvim_create_autocmd("VimEnter", {
  once = true,
  callback = function()
    vim.notify("Mnemosyne: usa :Tutor para practicar; <Esp>w guarda y <Esp>q sale")
  end,
})
