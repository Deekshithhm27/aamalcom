from odoo.exceptions import ValidationError,UserError
from odoo import models, fields, api,_

class CreateAccountMoveWizard(models.TransientModel):
    _name = 'batch.invoice.creation.wizard'
    _description = 'Create Account Move Wizard'

    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def create_account_move(self):
        draft_account_moves = self.env['draft.account.move'].search([
            ('client_parent_id', '=', self.client_parent_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),('state','=','draft')
        ])
        if not draft_account_moves:
            raise UserError(_('No records found.'))

        # Grouping of multiple lines inside an invoice
        consolidated_lines = []
        particulars = []
        particulars_lines = []
        employee_ids_added = set()
        for draft_move in draft_account_moves:
            consolidated_lines.append((0, 0, {
                'name':draft_move.service_enquiry_id.service_request_config_id.name,
                'employee_id': draft_move.employee_id.id,
                'service_enquiry_id':draft_move.service_enquiry_id.id,
                'quantity': 1,
                'price_unit': draft_move.untaxed_amount,
                'tax_ids': [(6, 0, draft_move.tax_ids.ids)],
            }))
            for line in draft_move.invoice_line_ids:
                if line.employee_id.id not in employee_ids_added:
                    particulars.append((0, 0, {
                        'employee_id': line.employee_id.id,
                    }))
                    employee_ids_added.add(line.employee_id.id)
            

        if consolidated_lines:
            new_account_move = self.env['account.move'].create({
                'partner_id': self.client_parent_id.id,
                'date': fields.Date.today(),
                'move_type': 'out_invoice',
                'invoice_type':'operation',
                'invoice_line_ids': consolidated_lines,
                'move_particulars_ids':particulars,
                'state':'draft'
            })

        for particular in new_account_move.move_particulars_ids:
            employee_id = particular.employee_id.id
            employee_lines = []
            for draft_move in draft_account_moves:
                for line in draft_move.invoice_line_ids:
                    if line.employee_id.id == employee_id:
                        employee_lines.append((0, 0, {
                            'name': line.name,
                            'amount':line.price_subtotal,
                            # Add other fields as needed
                        }))
            particular.write({'particulars_line_ids': employee_lines})


            for draft_move in draft_account_moves:
                draft_move.write({
                'invoiced_date': fields.Date.today(),
                'invoice_id': new_account_move.id,
                'state':'posted'
            })
            return {
                'type': 'ir.actions.act_window',
                'name': _('Success'),
                'res_model': 'invoice.created.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_message': _('Invoice is created successfully.')}
            }



        return {'type': 'ir.actions.act_window_close'}


class InvoiceCreatedWizard(models.TransientModel):
    _name = 'invoice.created.wizard'
    _description = 'Invoice Created Wizard'

    message = fields.Text(string='Message', readonly=True)

    def close_wizard(self):
        return {'type': 'ir.actions.act_window_close'}

# Track invoice againt service request or payroll or direct----------