# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def default_get(self,fields):
        res = super(HrEmployee,self).default_get(fields)
        salary_lines = [(5,0,0)]
        salary_ids = self.env['hr.client.salary.rule'].search([])
        for sal in salary_ids:
            line = (0,0,{
                'name':sal.id
                })
            salary_lines.append(line)
        res.update({
            'client_salary_rule_ids':salary_lines
            })
        return res


    client_salary_rule_ids = fields.One2many('emp.salary.line', 'employee_id', string="Salary Structure")

    confirm_salary_bool = fields.Boolean(string="Salary Details Confirmed",default=False)

    def confirm_salary_details(self):
        for employee in self:
            employee.confirm_salary_bool = True

            # Find an hr.payroll.structure record with payroll_type='external' and limit to 1
            struct_id = self.env['hr.payroll.structure'].search([('payroll_type', '=', 'external')], limit=1)
            contract_id = self.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')],limit=1)
            if contract_id:
                # Update the existing contract's state and date_end
                contract_id.write({
                    'state': 'close',
                    'date_end': (datetime.now() - timedelta(days=1)).date(),
                })

            # Create a new hr.contract.history record
            # contract_history = self.env['hr.contract.history'].create({
            #     'name': f"{employee.name} Contract History",
            # })

            # Create a contract record and add it to the contract_ids one2many field
            contract = self.env['hr.contract'].create({
                'name': f"{employee.name} Contract",
                'struct_id': struct_id.id,
                'employee_id':employee.id,
                'state':'open',
                'wage': employee.client_salary_rule_ids.filtered(lambda x: x.name.code == 'Basic').amount,
                'hra': employee.client_salary_rule_ids.filtered(lambda x: x.name.code == 'HRA').amount,
                'travel_allowance':employee.client_salary_rule_ids.filtered(lambda x: x.name.code == 'TA').amount,
                'other_allowance':employee.client_salary_rule_ids.filtered(lambda x: x.name.code == 'OA').amount,
                'hr_responsible_id':3
            })

            # contract_history.contract_ids = [(4, contract.id, False)]

    @api.onchange('client_salary_rule_ids')
    def update_salary_confirmation(self):
        for line in self:
            line.confirm_salary_bool = False


class EmpSalaryLines(models.Model):
    _name = "emp.salary.line"
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Employee Salary Line"

    name = fields.Many2one('hr.client.salary.rule',string="Structure Type")
    sequence = fields.Integer(string="Sequence",related="name.sequence",store=True)

    employee_id = fields.Many2one('hr.employee',string="Employee")
    
    amount = fields.Float(string="Amount")