# -*- coding:utf-8 -*-

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    client_payroll_inv = fields.Boolean(string='Client Payroll Invoice',default=False,help="This bool indicates that invoice created for clent against employee data for salary")
    salary_line_ids = fields.One2many('account.move.salary.line','move_sal_id',string="Salary Lines")

    def action_post(self):
        result = super(AccountMove, self).action_post()
        for sal_inv in self.salary_line_ids:
            sal_inv.salary_tracking_id.update({
                'is_invoiced':True,
                'invoice_id':self.id
                })

        return result

    # update is_invoiced on confirmation


class AccountMoveSalaryLine(models.Model):
    _name = 'account.move.salary.line'

    move_sal_id = fields.Many2one('account.move',string="Move id")

    salary_tracking_id = fields.Many2one('client.emp.salary.tracking',string="Salary Tracking")
    client_emp_sequence = fields.Char(string="Employee Id")
    gosi_charge = fields.Float(string="Gosi Charges")