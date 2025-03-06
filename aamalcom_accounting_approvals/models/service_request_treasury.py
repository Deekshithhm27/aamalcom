from odoo import models, fields


class ServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    account_move_id = fields.Many2one('account.move', string="Related Invoice")

    def action_upload_confirmation(self):
        result = super(ServiceRequestTreasury, self).action_upload_confirmation()
        for record in self:
            if record.account_move_id.move_type == 'in_invoice':
                record.account_move_id.upload_payment_doc = record.confirmation_doc
                record.account_move_id.is_confirmation_doc_uploaded = True
        return result
