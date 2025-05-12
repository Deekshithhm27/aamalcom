from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[('iqama_print', 'Iqama Print')], string="Service Requests", store=True, copy=False,
        required=True, ondelete={'iqama_print': 'cascade'})

    iqama_for = fields.Selection([
        ('self', 'Self'),
        ('family', 'Family')
    ], string='Iqama For?')
    dependent_iqama_id = fields.Binary(string="Upload Iqama")
    dependent_iqama_id_file_name = fields.Char(string="Upload Iqama File Name")

    iqama_scanned_doc = fields.Binary(string="Iqama Scanned Document")
    iqama_scanned_doc_file_name = fields.Char(string="Iqama Scanned Document File Name")
    iqama_scanned_doc_ref = fields.Char(string="Ref No.*")

    is_confirmation_given_to_client = fields.Boolean(default=False)
    is_action_iqama_uploaded = fields.Boolean(default=False)

    state = fields.Selection(
        selection_add=[('confirmation_doc_submitted', 'Confirmation Doc Submitted'),
                       ('iqama_state_updated', 'Iqama State Updated')],
        ondelete={'confirmation_doc_submitted': 'cascade', 'iqama_state_updated': 'cascade'})

    @api.onchange('service_request')
    def _onchange_service_request(self):
        for line in self:
            if line.service_request == 'iqama_print':
                line.aamalcom_pay = True

    def action_submit_initiate(self):
        result = super(ServiceEnquiry, self).action_submit_initiate()
        for record in self:
            if record.service_request == 'iqama_print':
                if record.iqama_for == 'self':
                    if not record.dependent_iqama_id:
                        raise ValidationError("Kindly Upload Iqama")
                elif record.iqama_for == 'family':
                    if not record.dependent_document_ids:
                        raise ValidationError("Kindly Update Dependent Documents")
                    # Check if person_name is added but dependent_iqama_id is missing
                    for dependent in record.dependent_document_ids:
                        if dependent.person_name and not dependent.dependent_iqama_id:
                            raise ValidationError(f"Kindly Update Dependent Iqama for {dependent.person_name}")
                else:
                    raise ValidationError("Kindly Update Iqama For for self/family")

                if record.aamalcom_pay and not (record.billable_to_client or record.billable_to_aamalcom):
                    raise ValidationError(
                        'Please select at least one billing detail when Fees to be paid by Aamalcom is selected.')
        return result

    def action_payment_confirmation_uploaded(self):
        for line in self:
            if line.service_request == 'iqama_print':
                if line.fee_receipt_doc and not line.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
                if line.confirmation_doc and not line.confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation Document")

                line.dynamic_action_status = 'Confirmation documents uploaded, Upload of Iqama scanned copy is pending.'
                line.state = 'confirmation_doc_submitted'

    def action_iqama_uploaded(self):
        for line in self:
            if line.service_request == 'iqama_print':
                if line.iqama_scanned_doc and not line.iqama_scanned_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Iqama Scanned Document")
                line.dynamic_action_status = 'Iqama scanned copy is uploaded, PM needs to sent confirmation to the client'
                line.is_action_iqama_uploaded = True
                line.state = 'iqama_state_updated'

    def action_confirmation_given_to_client(self):
        for line in self:
            if line.service_request == 'iqama_print':
                line.dynamic_action_status = 'Confirmation given to client on Iqama Print.PM needs to close the ticket'
                line.is_confirmation_given_to_client = True


class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")


