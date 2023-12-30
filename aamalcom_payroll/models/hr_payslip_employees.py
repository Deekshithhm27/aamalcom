# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    custom_employee_type = fields.Selection([('external','External'),('internal','Internal')],string="Employee Type",required=True)
    client_parent_id = fields.Many2one('res.partner',string="Client",domain=[('is_company','=',True)])
    external_employee_ids = fields.Many2many('hr.employee', 'ext_hr_employee_group_rel', 'ext_payslip_id', 'ext_employee_id', 'Employees',domain="[('custom_employee_type', '=', 'external'),('client_parent_id','=',client_parent_id)]")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',domain="[('custom_employee_type', '=', 'internal')]")

    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if data['custom_employee_type'] == 'external':
            if not data['external_employee_ids']:
                raise UserError(_("You must select employee(s) to generate payslip(s)."))
        if data['custom_employee_type'] == 'internal':
            if not data['employee_ids']:
                raise UserError(_("You must select employee(s) to generate payslip(s)."))
        if data['employee_ids']:
            # standard process for employees
            for employee in self.env['hr.employee'].browse(data['employee_ids']):
                slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
                res = {
                    'employee_id': employee.id,
                    'name': slip_data['value'].get('name'),
                    'struct_id': slip_data['value'].get('struct_id'),
                    'contract_id': slip_data['value'].get('contract_id'),
                    'payslip_run_id': active_id,
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                    'date_from': from_date,
                    'date_to': to_date,
                    'credit_note': run_data.get('credit_note'),
                    'company_id': employee.company_id.id,
                }
                payslips += self.env['hr.payslip'].create(res)
        else:
            # process for external employees
            # need to work on the duplicated tracking data and restrict to one per month
            for employee in self.env['hr.employee'].browse(data['external_employee_ids']):
                pay_data = self.env['client.emp.salary.tracking'].search([('date_start','>=',from_date),('date_end','<=',to_date),('employee_id','=',employee.id),('state','=','draft'),('is_invoiced','=',True)],limit=1)
                invoice_line_id = self.env['account.move'].search([('id','=',pay_data.invoice_id.id)])

                for line in invoice_line_id:
                    if line.amount_residual > 0:
                        raise UserError(_("Unable to proceed. Payment is not yet recieved"))

                if not pay_data:
                    raise UserError(_("Salary Details not found for %s for date range %s to %s")%(employee.name,from_date,to_date))

                slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)

                res = {
                    'employee_id': employee.id,
                    'name': slip_data['value'].get('name'),
                    'struct_id': slip_data['value'].get('struct_id'),
                    'contract_id': slip_data['value'].get('contract_id'),
                    'payslip_run_id': active_id,
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                    'worked_days_line_ids': [(0, 0, {
                        'name': _("Working Days"),
                        'sequence': 1,
                        'code': 'WORK100',
                        'number_of_days': pay_data.worked_days,
                        # 'number_of_hours': work_data['hours'],
                        'contract_id': pay_data.contract_id.id,
                    })],
                    'date_from': from_date,
                    'date_to': to_date,
                    'credit_note': run_data.get('credit_note'),
                    'company_id': employee.company_id.id,
                    'sal_track_id':pay_data.id
                }
                payslips += self.env['hr.payslip'].create(res)

        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def done_payslip_run(self):
        # this method is required to update the salary tracking status so as not to fetch the done record
        result = super(HrPayslipRun, self).done_payslip_run()
        for line in self.slip_ids:
            pay_data = self.env['client.emp.salary.tracking'].search([('date_start','>=',self.date_start),('date_end','<=',self.date_end),('employee_id','=',line.employee_id.id),('state','=','draft'),('is_invoiced','=',True)],limit=1)
            if pay_data:
                for pay in pay_data:
                    pay.update({
                        'state':'done'
                        })
        return result