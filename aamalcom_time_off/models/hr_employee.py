# aamalcom_time_off/models/hr_employee.py
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    religion = fields.Selection([
        ('muslim', 'Muslim'),
        ('non_muslim', 'Non Muslim'),
    ], string='Religion', default='non_muslim')