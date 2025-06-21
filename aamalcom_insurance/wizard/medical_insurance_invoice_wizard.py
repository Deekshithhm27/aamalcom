# File: aamalcom_insurance/models/insurance_invoice_wizard.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MedicalInsuranceInvoiceWizard(models.TransientModel):
    _name = 'medical.insurance.invoice.wizard'
    _description = 'Medical Insurance Invoice Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    client_parent_id = fields.Many2one('res.partner', string='Client', required=True,domain="[('is_company','=',True),('parent_id','=',False)]")

    def action_generate_invoice(self):
        self.ensure_one()
        domain = [
            ('insurance_activation_date', '>=', self.start_date),
            ('insurance_activation_date', '<=', self.end_date),
            ('client_parent_id', '=', self.client_parent_id.id),('state','=','draft')
        ]
        enrollment_lines = self.env['medical.insurance.invoice.details'].search(domain + [('insurance_type', '=', 'enrollment')])
        deletion_lines = self.env['medical.insurance.invoice.details'].search(domain + [('insurance_type', '=', 'deletion')])

        if not enrollment_lines and not deletion_lines:
        	raise UserError('No details in draft state to create invoice...')

        move_lines = []
        insurance_line_vals = []

        for line in enrollment_lines:
            insurance_line_vals.append((0, 0, {
                'employee_id': line.employee_id.id,
                'client_emp_sequence': line.client_emp_sequence,
                'iqama_no': line.iqama_no,
                'sponsor_id': line.sponsor_id,
                'insurance_activation_date': line.insurance_activation_date,
                'medical_class': line.medical_class,
                'total_amount': line.total_amount,
                'insurance_type': 'enrollment',
                'medical_insurance_invoice_id':line.id
            }))
            move_lines.append((0, 0, {
            	'employee_id': line.employee_id.id,
                'name': f"{line.employee_id.name or ''} - Enrollment ({line.medical_class or ''})",
                'quantity': 1,
                'price_unit': line.total_amount or 0.0,
            }))

        for line in deletion_lines:
            insurance_line_vals.append((0, 0, {
                'employee_id': line.employee_id.id,
                'client_emp_sequence': line.client_emp_sequence,
                'iqama_no': line.iqama_no,
                'sponsor_id': line.sponsor_id,
                'insurance_expiration_date': line.insurance_expiration_date,
                'medical_class': line.medical_class,
                'total_amount': line.total_amount,
                'insurance_type': 'deletion',
                'medical_insurance_invoice_id':line.id
            }))
            move_lines.append((0, 0, {
            	'employee_id': line.employee_id.id,
                'name': f"{line.employee_id.name or ''} - Deletion ({line.medical_class or ''})",
                'quantity': 1,
                'price_unit': line.total_amount or 0.0,
            }))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.client_parent_id.id,
            'invoice_type':'insurance',
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': move_lines,
            'medical_insurance_invoice_ids': insurance_line_vals,
        }

        invoice = self.env['account.move'].create(invoice_vals)
        if invoice:
        	(enrollment_lines + deletion_lines).write({'state': 'invoice_created','invoice_id': invoice.id})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Invoice Created'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }




class MedicalInsuranceInvoiceReportWizard(models.TransientModel):
    _name = 'medical.insurance.invoice.report.wizard'
    _description = 'Medical Insurance Report Print Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    client_parent_id = fields.Many2one('res.partner', string='Client', required=True,domain="[('is_company','=',True),('parent_id','=',False)]")

    def action_print_report(self):
        self.ensure_one()
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'client_parent_id': self.client_parent_id.id,
            'client_name': self.client_parent_id.name,
        }
        return self.env.ref('aamalcom_insurance.action_report_medical_insurance_summary').report_action(self, data=data)
