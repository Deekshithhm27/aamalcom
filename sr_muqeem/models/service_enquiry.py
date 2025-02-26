from datetime import date
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(selection_add=[('muqeem_dropout', 'Muqeem Dropout')],
                                       ondelete={'muqeem_dropout': 'cascade'})
    state = fields.Selection(selection_add=[('ere_valid', 'Valid ERE')], ondelete={'ere_valid': 'cascade'})

    is_inside_ksa = fields.Boolean(string="Inside KSA",
                                    help="Indicates whether the employee is Inside KSA (True) or Outside KSA (False).")
    expiry_of_ere = fields.Date(string="Expiry of ERE", help="Expiry date of the employee's ERE")

    muqeem_confirmation_doc = fields.Binary(string="Confirmation Document")
    muqeem_confirmation_doc_file_name = fields.Char(string="Confirmation Document File Name")
    muqeem_confirmation_doc_ref = fields.Char(string="Ref No.*")

    is_resubmission = fields.Boolean(default=False)

    # @api.constrains('is_inside_ksa', 'expiry_of_ere')
    # def _check_outside_ksa(self):
    #     for line in self:
    #         if line.service_request in 'muqeem_dropout':
    #             if line.is_inside_ksa:
    #                 raise ValidationError("Not applicable for employees inside KSA. Only applicable for those outside KSA.")

    def action_submit_initiate(self):
        result = super(ServiceEnquiry, self).action_submit_initiate()
        for line in self:
            if line.service_request in 'muqeem_dropout':
                if not line.is_inside_ksa and not line.expiry_of_ere:
                    raise ValidationError("Kindly Update Expiry of ERE")
                if line.is_resubmission:
                    line.dynamic_action_status = 'Ticket resubmitted, Employee needs to be assigned by PM'
        return result

    def action_valid_ere(self):
        """Change status to 'ERE is Valid' and notify the client SPOC"""
        for line in self:
            if line.service_request in 'muqeem_dropout':
                line.state = 'ere_valid'
                line.dynamic_action_status = 'ERE is still valid,Please re initiate this process upon ERE expiry.'
                line.assign_govt_emp_one = False
                line.assigned_govt_emp_one = False
                line.is_resubmission = True

                partner_id = line.client_id.id
                user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
                if user:
                    line.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=user.id,
                        summary="ERE Still Valid - Action Required(Cancel)",
                        note="The ERE is still valid. The request can be re initiated after expiry on."
                    )

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in 'muqeem_dropout':
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
                if record.muqeem_confirmation_doc and not record.muqeem_confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation Document")
                invoice_line_ids = []
                for line in record.service_enquiry_pricing_ids:
                    invoice_line_ids.append((0, 0, {
                        'name': line.name,
                        'employee_id': record.employee_id.id,
                        'price_unit': line.amount,
                        'quantity': 1,
                        'service_enquiry_id': record.id
                    }))

                # Create draft.account.move record
                account_move = self.env['draft.account.move'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id': record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id': record.employee_id.id,
                    'move_type': 'service_ticket',
                    'invoice_line_ids': invoice_line_ids,
                })
        return result
