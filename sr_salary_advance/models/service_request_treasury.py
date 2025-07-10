from odoo import models, fields, api
class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    service_request_type = fields.Selection(
        related="service_request_id.service_request",
        store=True,
        readonly=True,
    )

    employee_bank_account_number = fields.Char(
        string="Employee Bank Account",
        related='employee_id.bank_account_id.acc_number', # This is the key part!
        readonly=True, # It's a related field, so it should be readonly
        store=False,  # Set to True if you want to store it in the DB (less common for related fields)
        help="Bank Account Number of the Employee associated with this service request."
    )
    employee_bank_id = fields.Many2one(
            'res.bank',
            string="Employee Bank",
            compute="_compute_employee_bank_details",
            store=False,
            readonly=True
        )
    employee_bic = fields.Char(
        string="Employee IBAN",
        compute="_compute_employee_bank_details",
        store=False,
        readonly=True
    )

    @api.depends('employee_id')
    def _compute_employee_bank_details(self):
        for record in self:
            # Removed: record.employee_bank_id = False
            # Removed: record.employee_bic = False
            
            if record.employee_id:
                visa_record = self.env['employment.visa'].search([
                    ('employee_id', '=', record.employee_id.id)
                ], limit=1)
                
                if visa_record:
                    record.employee_bank_id = visa_record.bank_id.id
                    record.employee_bic = visa_record.bic
                else: # Add this else block to clear fields if no visa_record is found
                    record.employee_bank_id = False
                    record.employee_bic = False
            else: # Add this else block to clear fields if employee_id is not set
                record.employee_bank_id = False
                record.employee_bic = False

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
            