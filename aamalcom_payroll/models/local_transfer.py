# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class LocalTransfer(models.Model):
    _inherit = 'local.transfer'
    

    @api.model
    def default_get(self,fields):
        res = super(LocalTransfer,self).default_get(fields)
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

    client_salary_rule_ids = fields.One2many('salary.line', 'local_transfer_id', string="Salary Structure")


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        # this method is used to update salary details from employee master
        if self.employee_id:
            employee = self.employee_id

            # Loop through the client_salary_rule_ids in hr.employee
            for employee_salary_line in employee.client_salary_rule_ids:
                # Search for an existing record in local.transfer with the same name
                existing_record = self.client_salary_rule_ids.filtered(
                    lambda x: x.name == employee_salary_line.name
                )

                if existing_record:
                    # Update the amount of the existing record
                    existing_record.amount = employee_salary_line.amount
                else:
                    # If no existing record with the same name is found, create a new one
                    self.client_salary_rule_ids = [(0, 0, {
                        'name': employee_salary_line.name,
                        'amount': employee_salary_line.amount,
                    })]
