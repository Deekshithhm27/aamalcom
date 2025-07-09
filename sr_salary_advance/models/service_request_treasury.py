from odoo import models, fields, api
class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    employee_bank_account_number = fields.Char(
        string="Employee Bank Account",
        related='employee_id.bank_account_id.acc_number', # This is the key part!
        readonly=True, # It's a related field, so it should be readonly
        store=False,  # Set to True if you want to store it in the DB (less common for related fields)
        help="Bank Account Number of the Employee associated with this service request."
    )
    def action_upload_confirmation(self):
        # Call the super method to keep the existing functionality
        super(InheritedServiceRequestTreasury, self).action_upload_confirmation()

        # Add custom logic for 'salary_advance'
        for line in self:
            if line.service_request_id.service_request == 'salary_advance':
                # Upload confirmation_doc to the service.request model
                line.service_request_id.write({'upload_payment_doc': line.confirmation_doc})
                line.service_request_id.write({'payment_doc_ref':line.confirmation_doc_ref})

                # Only modify dynamic_action_status if the state is 'approved'
                if line.service_request_id.state == 'approved':
                    # Set the specific dynamic action status for 'salary_advance'
                    line.service_request_id.dynamic_action_status = "Service request approved by Finance Team. Process needs to be completed by PM."
                    line.service_request_id.action_user_id = line.service_request_id.approver_id.user_id.id
            