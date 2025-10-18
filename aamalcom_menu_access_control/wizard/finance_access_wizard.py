from odoo import models, fields, api, _

class FinanceAccessWizard(models.TransientModel):
    _name = "finance.access.wizard"
    _description = "Finance Access Wizard"

    @api.model
    def _get_finance_menus(self):
        """Return only menus under Accounting root menu"""
        try:
            account_root = self.env.ref('account.menu_finance')  # Odoo Accounting root
        except ValueError:
            # fallback if the XML ID is not found
            account_root = self.env['ir.ui.menu']
        return self.env['ir.ui.menu'].search([('id', 'child_of', account_root.id)])


    menu_ids = fields.Many2many('ir.ui.menu', string="Finance Menus",domain=lambda self: [('id', 'in', self._get_finance_menus().ids)])
    level_id = fields.Many2one('finance.access.level', string="Access Level", required=True)

    def action_apply_access(self):
        employees = self.level_id.employee_ids
        users = employees.mapped('user_id')

        # Ensure a group exists for this level
        group_name = f"Finance {self.level_id.name}"
        group = self.env['res.groups'].search([('name', '=', group_name)], limit=1)
        if not group:
            group = self.env['res.groups'].create({
                'name': group_name,
                'category_id': self.env.ref('base.module_category_accounting_finance').id
            })

        # Assign menus to group
        for menu in self.menu_ids:
            # menu.groups_id = [(6, 0, [group.id])]
            old_groups = menu.groups_id
            menu.groups_id = [(6, 0, [group.id])]
            new_groups = menu.groups_id

            # Create history record
            self.env['menu.access.history'].create({
            	'name': f"{menu.name} access updated on {fields.Datetime.now().strftime('%d-%b-%Y %H:%M')} by {self.env.user.name}",
                'menu_id': menu.id,
                'level_id': self.level_id.id,
                'changed_by': self.env.user.id,
                'old_group_ids': [(6, 0, old_groups.ids)],
                'new_group_ids': [(6, 0, new_groups.ids)],
                'changed_on': fields.Datetime.now(),
            })

        # Assign group to users in this level
        for user in users:
            user.groups_id = [(4, group.id)]
