from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('passport_info_update', 'Passport Information Update')
        ],
        string="Service Requests",
        store=True,
        copy=False
    )
    
    upload_new_passport_doc = fields.Binary(string="New Passport Document")
    upload_new_passport_doc_file_name = fields.Char(string="New Passport Doc")
    upload_old_passport_doc = fields.Binary(string="Old Passport Document")
    upload_old_passport_doc_file_name = fields.Char(string="Old Passport Doc")
    upload_muqeem_doc = fields.Binary(string="Muqeem Document")
    upload_muqeem_doc_file_name = fields.Char(string="Muqeem Document")
    muqeem_doc_ref = fields.Char(string="Ref No.*")
    muqeem_points = fields.Integer(string="Points")
    

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_new_passport_doc' in vals:
            vals['upload_new_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NewPassportDoc.pdf"
        if 'upload_old_passport_doc' in vals:
            vals['upload_old_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_OldPassportDoc.pdf"
        if 'fee_receipt_doc' in vals:
            vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceiptDoc.pdf"
        if 'upload_muqeem_doc' in vals:
            vals['upload_muqeem_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_new_passport_doc' in vals:
                vals['upload_new_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_NewPassportDoc.pdf"
            if 'upload_old_passport_doc' in vals:
                vals['upload_old_passport_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_OldPassportDoc.pdf"
            if 'fee_receipt_doc' in vals:
                vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceiptDoc.pdf"
            if 'upload_muqeem_doc' in vals:
                vals['upload_muqeem_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)    

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'passport_info_update':
                if not line.upload_new_passport_doc:
                    raise ValidationError(_("Please upload the new passport document."))
                if not line.upload_old_passport_doc:
                    raise ValidationError(_("Please upload the old passport document."))
                spoc_name = self.env.user.company_spoc_id.name if self.env.user.company_spoc_id else 'Unknown SPOC'
                line.dynamic_action_status = _(f"Passport update request submitted for review by: {spoc_name}")
        return True

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in 'passport_info_update':
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Document")
                if record.upload_muqeem_doc and not record.muqeem_doc_ref:
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


class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")
