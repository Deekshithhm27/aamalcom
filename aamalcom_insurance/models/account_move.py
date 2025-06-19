from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMOve(models.Model):
    _inherit = 'account.move'

    insurance_reimbursement_id = fields.Many2one('insurance.reimbursement',string="Reimbursement Ref")

