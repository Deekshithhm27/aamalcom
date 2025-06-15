from odoo import models, fields, api

class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    
    def action_upload_confirmation(self):
        # Call the super method to keep the existing functionality
        super(InheritedServiceRequestTreasury, self).action_upload_confirmation()

        # Add custom logic for 'dependents_ere'
        for line in self:
            if line.service_request_id.service_request == 'dependents_ere':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})
                if line.service_request_id.state == 'done':
                    line.service_request_id.dynamic_action_status = "Process completed"
                    line.action_user_id= False

     ##this method use to close ticket after doc is uploaded from treasur dept in SR depenednet ere           
    def write(self, vals):
        res = super(InheritedServiceRequestTreasury, self).write(vals)
        if vals.get('state') == 'done':
            for record in self:
                service_request = record.service_request_id
                if service_request and service_request.service_request == 'dependents_ere':
                    service_request.write({
                    'state': 'done',
                    'dynamic_action_status': "Process Completed",
                        })
        return res

            