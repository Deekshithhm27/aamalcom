from odoo import models, fields, api
class InheritedServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    service_request_type = fields.Selection(
        related="service_request_id.service_request",
        store=True,
        readonly=True,
    )

    nature_of_advance = fields.Text("Nature of Advance")

    employee_bank_account_number = fields.Char(
        string="Employee Bank Account ID",
        compute='_compute_employee_bank_details',
        store=False
    )

    employee_bank_id = fields.Many2one(
        'res.bank',
        string="Employee Bank",
        compute='_compute_employee_bank_details',
        store=False
    )

    

    @api.depends('employee_id')
    def _compute_employee_bank_details(self):
        for rec in self:
            bank_account = rec.employee_id.bank_ids[:1]  # take first bank account
            rec.employee_bank_account_number = bank_account.acc_number if bank_account else False
            rec.employee_bank_id = bank_account.bank_id if bank_account else False

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
            