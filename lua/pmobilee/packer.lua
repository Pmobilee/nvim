-- This file can be loaded by calling `lua require('plugins')` from your init.vim

-- Only required if you have packer configured as `opt`
vim.cmd [[packadd packer.nvim]]

return require('packer').startup(function(use)
    -- Packer can manage itself
    use 'wbthomason/packer.nvim'

    use {
        'nvim-telescope/telescope.nvim', tag = '0.1.8',
        requires = { {'nvim-lua/plenary.nvim'} }
    }
    use('nvim-treesitter/nvim-treesitter', {run = ':TSUpdate'})
    use('theprimeagen/harpoon')
    use('mbbill/undotree')
    use('tpope/vim-fugitive')

    -- LSP and autocompletion plugins
    use 'neovim/nvim-lspconfig' -- LSP
    use {
        'williamboman/mason.nvim',
        opts = {ensure_installed = {'pyright', 'black', 'mypy', 'ruff'}}
    }
    use 'williamboman/mason-lspconfig.nvim' -- Mason LSP config
    use 'hrsh7th/nvim-cmp' -- Autocompletion plugin
    use 'hrsh7th/cmp-nvim-lsp' -- LSP source for nvim-cmp
    use 'hrsh7th/cmp-buffer' -- Buffer source for nvim-cmp
    use 'hrsh7th/cmp-path' -- Path source for nvim-cmp
    use 'saadparwaiz1/cmp_luasnip' -- Snippet source for nvim-cmp
    use 'L3MON4D3/LuaSnip' -- Snippets plugin
    use 'rafamadriz/friendly-snippets' -- Preconfigured snippets

    -- Python-specific tools
    use 'mfussenegger/nvim-lint' -- Linting
    use 'jose-elias-alvarez/null-ls.nvim' -- Formatters and linters as LSP

    -- Additional plugins for better integration
    use 'nvim-lua/plenary.nvim' -- Common utilities
    use { "catppuccin/nvim", as = "catppuccin" }
    use { 'nvim-telescope/telescope-themes.nvim' } -- Theme browser

        -- Additional themes
    use 'morhetz/gruvbox' -- Gruvbox theme
    use 'joshdick/onedark.vim' -- OneDark theme
    use 'folke/tokyonight.nvim' -- TokyoNight theme
    use 'EdenEast/nightfox.nvim' -- Nightfox theme
    use 'dracula/vim' -- Dracula theme
end)

