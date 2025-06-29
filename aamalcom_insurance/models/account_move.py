from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    insurance_reimbursement_id = fields.Many2one('insurance.reimbursement',string="Reimbursement Ref")
    invoice_type = fields.Selection(
        selection_add=[('insurance', 'Insurance')],
        ondelete={'insurance': 'cascade'}
    )


    medical_insurance_invoice_ids = fields.One2many(
        'account.move.insurance.line', 'med_move_id',
        string='Medical Insurance Invoice Details'
    )
    life_insurance_invoice_ids = fields.One2many(
        'account.move.life.insurance.line', 'life_move_id',
        string='Life Insurance Invoice Details'
    )
    insurance_inv_ref = fields.Char(string="Insurance Inv Ref")

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.medical_insurance_invoice_ids:
                rec.medical_insurance_invoice_ids.mapped('medical_insurance_invoice_id').write({'state': 'invoiced'})
            if rec.life_insurance_invoice_ids:
                rec.life_insurance_invoice_ids.mapped('life_insurance_invoice_id').write({'state': 'invoiced'})
        return res



class AccountMoveInsuranceLine(models.Model):
    _name = 'account.move.insurance.line'
    _description = 'Insurance Line in Invoice'

    med_move_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee')
    client_emp_sequence = fields.Char(string="Employee Number")
    iqama_no = fields.Char(string="Iqama Number")
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Id")
    insurance_activation_date = fields.Date(string='Insurance Activation Date')
    insurance_expiration_date = fields.Date(string='Insurance Expiration Date')
    medical_class = fields.Char(string='Medical Class')
    total_amount = fields.Float(string='Total Amount')
    insurance_type = fields.Selection([
        ('enrollment', 'Enrollment'),
        ('deletion', 'Deletion')
    ], string='Insurance Type')
    medical_insurance_invoice_id = fields.Many2one('medical.insurance.invoice.details')

class AccountMoveLifeInsuranceLine(models.Model):
    _name = 'account.move.life.insurance.line'
    _description = 'Life Insurance Line in Invoice'

    life_move_id = fields.Many2one('account.move', string='Invoice', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee')
    client_emp_sequence = fields.Char(string="Employee Number")
    iqama_no = fields.Char(string="Iqama Number")
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Id")
    insurance_activation_date = fields.Date(string='Insurance Activation Date')
    insurance_expiration_date = fields.Date(string='Insurance Expiration Date')
    medical_class = fields.Char(string='Medical Class')
    total_amount = fields.Float(string='Total Amount')
    insurance_type = fields.Selection([
        ('enrollment', 'Enrollment'),
        ('deletion', 'Deletion')
    ], string='Insurance Type')
    life_insurance_invoice_id = fields.Many2one('life.insurance.invoice.details')
