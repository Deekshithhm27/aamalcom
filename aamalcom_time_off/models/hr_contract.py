# aamalcom_time_off/models/hr_contract.py
from odoo import fields, models

class HrContract(models.Model):
    _inherit = 'hr.contract'

    frozen = fields.Boolean(string='Frozen', default=False)