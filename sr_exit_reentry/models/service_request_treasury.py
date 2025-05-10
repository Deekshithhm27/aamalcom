from odoo import models, fields


class ServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    def action_upload_confirmation(self):
        result = super(ServiceRequestTreasury, self).action_upload_confirmation()
        for record in self:
            if record.service_request_id.service_request == 'exit_reentry_issuance_ext' and record.service_request_id.aamalcom_pay == True:
                record.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                record.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                record.service_request_id.dynamic_action_status = "Approved & payment confirmation by finance manager.Employee needs to be assigned by PM."
        return result
