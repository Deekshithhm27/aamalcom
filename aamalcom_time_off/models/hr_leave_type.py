# aamalcom_time_off/models/hr_leave_type.py
from odoo import fields, models

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    fixed_days = fields.Float(string='Fixed Duration (Days)', help='If set, leaves of this type must have this exact duration.')