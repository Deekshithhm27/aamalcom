from odoo.exceptions import ValidationError,UserError
from odoo import models, fields, api,_

class CreateAccountMoveWizard(models.TransientModel):
    _name = 'batch.invoice.creation.wizard'
    _description = 'Create Account Move Wizard'

    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True)]")
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

        consolidated_lines = []
        for draft_move in draft_account_moves:
            for line in draft_move.invoice_line_ids:
                consolidated_lines.append((0, 0, {
                    'employee_id': line.employee_id.id,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],  # Copy the tax_ids from draft.account.move.line

                    # Add other fields as needed
                }))
            # Update the invoice_date in the draft account move
            

        if consolidated_lines:
            new_account_move = self.env['account.move'].create({
                'partner_id': self.client_parent_id.id,
                'date': fields.Date.today(),
                'move_type': 'out_invoice',  # Set the appropriate move type
                'invoice_line_ids': consolidated_lines,
                'state':'draft'
            })
            for draft_move in draft_account_moves:
                draft_move.write({
                'invoiced_date': fields.Date.today(),
                'invoice_id': new_account_move.id,
                'state':'posted'
            })



        return {'type': 'ir.actions.act_window_close'}

