from odoo import models, fields, api

class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'



    def action_upload_confirmation(self):
        # Call the super method to keep the existing functionality
        super(InheritedServiceRequestTreasury, self).action_upload_confirmation()
        # Add custom logic for 'ajeer_permit'
        for line in self:
            if line.service_request_id.service_request == 'iqama_correction':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                # Only modify dynamic_action_status if the state is 'approved'
                # if line.service_request_id.state == 'approved':
                    # Set the specific dynamic action status for 'ajeer_permit'
                line.service_request_id.dynamic_action_status = "Service request approved by Finance Team.PM needs to close the ticket"
                line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
                line.service_request_id.write({'processed_date': fields.Datetime.now()})
            