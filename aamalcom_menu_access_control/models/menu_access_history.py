from odoo import models, fields, api
from datetime import datetime

class MenuAccessHistory(models.Model):
    _name = "menu.access.history"
    _description = "Menu Access History"
    _order = "create_date desc"

    name = fields.Char(string="Name")

    menu_id = fields.Many2one('ir.ui.menu', string="Menu", required=True)
    level_id = fields.Many2one('finance.access.level', string="Access Level", required=True)
    changed_by = fields.Many2one('res.users', string="Changed By", default=lambda self: self.env.user)
    old_group_ids = fields.Many2many('res.groups','old_group_id', string="Old Groups")
    new_group_ids = fields.Many2many('res.groups','new_group_id', string="New Groups")
    changed_on = fields.Datetime(string="Changed On", default=fields.Datetime.now)
