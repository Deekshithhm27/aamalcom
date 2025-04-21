from odoo import models, fields, api

class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    total_amount = fields.Monetary(string="Price", compute="_compute_total_amount", store=True, currency_field='currency_id')

    @api.depends('service_request_id.service_request', 'service_request_id.salary_advance_amount')
    def _compute_total_amount(self):
        for record in self:
            if record.service_request_id.service_request == 'salary_advance':
                record.total_amount = record.service_request_id.salary_advance_amount
            else:
                record.total_amount = 0  # Or another value if necessary

    def action_upload_confirmation(self):
        # Call the super method to keep the existing functionality
        super(InheritedServiceRequestTreasury, self).action_upload_confirmation()

        # Add custom logic for 'salary_advance'
        for line in self:
            if line.service_request_id.service_request == 'salary_advance':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})

                # Only modify dynamic_action_status if the state is 'approved'
                if line.service_request_id.state == 'approved':
                    # Set the specific dynamic action status for 'salary_advance'
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. Process needs to be completed by PM."

            # Ensure that other service requests don't get the 'salary_advance' message
            elif line.service_request_id.service_request not in ['salary_advance']:
                # Default dynamic action status for other service requests
                if line.service_request_id.state == 'approved':
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. First govt employee needs to be assigned by PM."
