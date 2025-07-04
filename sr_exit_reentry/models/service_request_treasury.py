from odoo import models, fields


class ServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    def action_upload_confirmation(self):
        result = super(ServiceRequestTreasury, self).action_upload_confirmation()
        for record in self:
            if record.service_request_id.service_request == 'exit_reentry_issuance':
                record.service_request_id.write({'upload_payment_doc': record.confirmation_doc})
                record.service_request_id.write({'payment_doc_ref':record.confirmation_doc_ref})
                record.service_request_id.dynamic_action_status = "Approved by finance manager.Employee needs to be assigned by PM."
                record.service_request_id.action_user_id = record.service_request_id.approver_id.user_id.id
                record.service_request_id.write({'processed_date': fields.Datetime.now()})

            elif record.service_request_id.service_request == 'exit_reentry_issuance_ext' and record.service_request_id.aamalcom_pay == True:
                record.service_request_id.write({'upload_payment_doc': record.confirmation_doc})
                record.service_request_id.write({'payment_doc_ref':record.confirmation_doc_ref})
                record.service_request_id.dynamic_action_status = "Approved by finance manager.Employee needs to be assigned by PM."
                record.service_request_id.action_user_id = record.service_request_id.approver_id.user_id.id
                record.service_request_id.write({'processed_date': fields.Datetime.now()})

        return result
