-- Null-ls setup
local null_ls = require('null-ls')

null_ls.setup({
    sources = {
        null_ls.builtins.diagnostics.ruff,
        null_ls.builtins.formatting.black,
    },
    -- Format on save
    on_attach = function(client, bufnr)
        if client.server_capabilities.documentFormattingProvider then
            -- Ensure the "AutoFormat" augroup exists
            local group_id = vim.api.nvim_create_augroup("AutoFormat", { clear = true })
            
            vim.api.nvim_create_autocmd("BufWritePost", {
                group = group_id,
                buffer = bufnr,
                callback = function()
                    vim.lsp.buf.format({ bufnr = bufnr })
                end,
            })
        end
    end,
})

