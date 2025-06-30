from odoo import models, fields, api
from odoo.exceptions import UserError

class InsuranceReimbursement(models.Model):
    _name = 'insurance.reimbursement'
    _description = 'Insurance Reimbursement'

    name = fields.Char(string="Reference", default="New", readonly=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    client_parent_id = fields.Many2one('res.partner',string="Client", required=True,domain="[('is_company','=',True),('parent_id','=',False)]")
    insurance_inv_ref = fields.Char(string="Insurance Ref")
    employee_id = fields.Many2one('hr.employee', required=True,domain="[('client_parent_id', '=', client_parent_id)]")
    amount = fields.Monetary(string='Amount to Reimburse', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft',string="Status",tracking=True,copy=False)

    credit_note_id = fields.Many2one('account.move', string="Credit Note", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.reimbursement') or 'New'
        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            if not rec.amount:
                raise UserError("Amount must be set before confirming.")
            move = self.env['account.move'].create({
                'move_type': 'out_refund',
                'insurance_inv_ref': rec.insurance_inv_ref,
                'partner_id': rec.client_parent_id.id,
                'invoice_date': fields.Date.today(),
                'invoice_origin': f"Reimbursement for {rec.employee_id.name}",
                'invoice_type':'insurance',
                'insurance_inv_ref':rec.insurance_inv_ref,
                'insurance_reimbursement_id':rec.id,
                'invoice_line_ids': [(0, 0, {
                    'employee_id':rec.employee_id.id,
                    'name': f"Reimbursement for {rec.employee_id.name}",
                    'quantity': 1,
                    'price_unit': rec.amount,
                })],
            })
            rec.write({
                'state': 'confirmed',
                'credit_note_id': move.id,
            })

