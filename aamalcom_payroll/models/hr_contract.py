# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'

    travel_allowance = fields.Monetary(string="Transportation Allowance", help="Travel allowance")
    other_deductions = fields.Monetary(string="Other Deductions", help="Other Deductions")
    arrears = fields.Monetary(string="Arrears",help="Arrears")
    advances = fields.Monetary(string="Advances",help="Advances")
    overtime = fields.Monetary(string="Overtime",help="Overtime")
    additions = fields.Monetary(string="Additions",help="Additions")