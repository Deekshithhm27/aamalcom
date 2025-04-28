from odoo import models, fields, api

class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    total_amount = fields.Monetary(
        string="Price", 
        compute="_compute_total_amount", 
        store=True, 
        currency_field='currency_id'
    )


    def action_upload_confirmation(self):
        # Call the super method to keep the existing functionality
        super(InheritedServiceRequestTreasury, self).action_upload_confirmation()
        # Add custom logic for 'ajeer_permit'
        for line in self:
            if line.service_request_id.service_request == 'ajeer_permit':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                # Only modify dynamic_action_status if the state is 'approved'
                if line.service_request_id.state == 'approved':
                    # Set the specific dynamic action status for 'ajeer_permit'
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team.1st govt employee Needs to uplaod Ajeer Intimation doc"
            # Ensure that other service requests don't get the 'ajeer_permit' message
            elif line.service_request_id.service_request not in ['ajeer_permit']:
                # Default dynamic action status for other service requests
                if line.service_request_id.state == 'approved':
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. First govt employee need to be assigned by PM."
