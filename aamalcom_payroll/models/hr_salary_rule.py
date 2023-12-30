# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrPayrollStructure(models.Model):
    """
    Salary structure used to defined
    - Basic
    - Allowances
    - Deductions
    """
    _inherit = 'hr.payroll.structure'

    payroll_type = fields.Selection([('internal','Internal'),('external','External')],default="internal",tracking=True)