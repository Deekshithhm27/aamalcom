from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ClientEmpSalaryTrackingWizard(models.TransientModel):
    _name = 'client.emp.salary.tracking.wizard'
    _description = 'Generate Invoice for Employee Salary Tracking'

    client_parent_id = fields.Many2one('res.partner',string="Client",required=True,domain=[('is_company','=',True)])
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)

    def generate_invoice(self):
        for wizard in self:
            employee_domain = [
                ('date_start', '>=', wizard.date_start),
                ('date_end', '<=', wizard.date_end),
                ('client_parent_id','=',wizard.client_parent_id.id),('is_invoiced','=',False),('state','=','draft')
            ]
            employee_records = self.env['client.emp.salary.tracking'].search(employee_domain)
            if not employee_records:
                raise UserError("No Payroll data to invoice for selected date range")
            gosi_charge = self.env['gosi.charges'].search([('name','!=',False)],limit=1)

            basic_salary = sum(employee_records.mapped('wage'))
            hra = sum(employee_records.mapped('hra'))
            sum_gosi_charges = sum(employee_records.mapped('gosi_charges'))
            # gosi_inv_charge = ((basic_salary + hra) * float(gosi_charge.name))/100
            gosi_inv_charge = sum_gosi_charges

            gross_salary = sum(employee_records.mapped('gross_salary'))

            journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()

            # Create an invoice for the client
            invoice = self.env['account.move'].create({
                'partner_id': wizard.client_parent_id.id,
                'move_type': 'out_invoice',  # or 'in_invoice' depending on your use case
                'state':'draft',
                'journal_id':journal.id,
                'client_payroll_inv':True,
                'invoice_line_ids': [(0, 0, {
                    'name':"Salary of %s Employees" % len(employee_records),
                    'price_unit': gross_salary + gosi_inv_charge,
                    'quantity': 1.0,
                    # 'analytic_account_id': False,
                })],
            })
            for employee_record in employee_records:
                self.env['account.move.salary.line'].create({
                    'move_sal_id': invoice.id,
                    'salary_tracking_id': employee_record.id,
                    # 'gosi_charge': ((employee_record.wage + employee_record.hra)* float(gosi_charge.name))/100,
                    'gosi_charge': employee_record.gosi_charges,
                    'client_emp_sequence': employee_record.client_emp_sequence,
                })
