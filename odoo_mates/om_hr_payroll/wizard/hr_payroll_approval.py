from odoo import fields, models, api

class HrPayrollApprovalWizard(models.TransientModel):
    _name = 'hr.payroll.approval.wizard'
    _description = 'Payslip Approval Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)

    def submit_for_approval(self):
        payslips = self.env['hr.payslip'].search([
            
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
            ('state', 'in', ['draft', 'verify'])
        ])

        if payslips:
            # Change the state to the correct value
            payslips.write({'state': 'submit_to_payroll'}) 
        return {'type': 'ir.actions.act_window_close'}