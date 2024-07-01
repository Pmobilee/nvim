-- LSP setup
local lspconfig = require('lspconfig')
local mason = require('mason')
local mason_lspconfig = require('mason-lspconfig')

mason.setup()
mason_lspconfig.setup({
    ensure_installed = { 'pyright' },
})

lspconfig.pyright.setup{}

-- -- Null-ls setup
local null_ls = require('null-ls')

null_ls.setup({
    sources = {
        null_ls.builtins.diagnostics.ruff,
        null_ls.builtins.formatting.ruff, -- Use ruff for formatting
        null_ls.builtins.formatting.black, -- Optionally use black for formatting
    },
    -- Format on save
    on_attach = function(client, bufnr)
        if client.server_capabilities.documentFormattingProvider then
            vim.cmd([[
                augroup LspFormatting
                    autocmd! * <buffer>
                    autocmd BufWritePre <buffer> lua vim.lsp.buf.format({ timeout_ms = 2000 })
                augroup END
            ]])
        end
    end,
})

-- Completion setup
local cmp = require('cmp')
cmp.setup({
    snippet = {
        expand = function(args)
            require('luasnip').lsp_expand(args.body)
        end,
    },
    mapping = {
        ['<C-b>'] = cmp.mapping.scroll_docs(-4),
        ['<C-f>'] = cmp.mapping.scroll_docs(4),
        ['<C-Space>'] = cmp.mapping.complete(),
        ['<C-e>'] = cmp.mapping.abort(),
        ['<CR>'] = cmp.mapping.confirm({ select = true }),
    },
    sources = cmp.config.sources({
        { name = 'nvim_lsp' },
        { name = 'luasnip' },
    }, {
        { name = 'buffer' },
    })
})

-- nvim-lint setup
local lint = require('lint')
lint.linters_by_ft = {
    python = {'ruff'},
}

vim.api.nvim_command('au BufWritePost <buffer> lua require("lint").try_lint()')

