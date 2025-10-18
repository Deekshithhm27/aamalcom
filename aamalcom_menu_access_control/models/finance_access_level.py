from odoo import models, fields

class FinanceAccessLevel(models.Model):
    _name = "finance.access.level"
    _description = "Finance Access Level"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Level Name", required=True)
    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees in this Level",tracking=True,domain="[('custom_employee_type', '=', 'internal')]"
    )
