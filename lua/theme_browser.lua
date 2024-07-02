local M = {}

function M.browse_themes()
    local themes = require('telescope.themes')
    local builtin = require('telescope.builtin')
    local finders = require('telescope.finders')
    local pickers = require('telescope.pickers')
    local sorters = require('telescope.sorters')
    local actions = require('telescope.actions')
    local action_state = require('telescope.actions.state')

    local theme_list = {
        'catppuccin',
        -- Add other themes you have installed here
        'gruvbox',
        'catppuccin-mocha',
         'onedark',
         'tokyonight',
         'nightfox',
         'dracula'
        -- etc.
    }

    pickers.new({}, {
        prompt_title = 'Browse Themes',
        finder = finders.new_table {
            results = theme_list,
        },
        sorter = sorters.get_generic_fuzzy_sorter(),
        attach_mappings = function(_, map)
            map('i', '<CR>', function(prompt_bufnr)
                local selection = action_state.get_selected_entry()
                actions.close(prompt_bufnr)
                vim.cmd('colorscheme ' .. selection[1])
            end)
            return true
        end,
    }):find()
end

return M

