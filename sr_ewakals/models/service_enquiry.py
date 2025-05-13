from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('e_wakala', 'E-Wakala'),
            ('cancelled_e_wakala', 'Cancellation E-Wakala')
        ],
        string="Service Request",
        store=True,
        copy=False,ondelete={
            'e_wakala': 'cascade',
            'cancelled_e_wakala': 'cascade'
            
        }
    )

    block_visa_doc = fields.Binary(string="Block Visa Document")
    block_visa_doc_file_name = fields.Char(string="Block Visa Document")
    attached_issued_visa_doc = fields.Binary(string="Issued Visa Document")
    attached_issued_visa_doc_ref = fields.Char(string="Ref No")
    attached_issued_visa_doc_file_name = fields.Char(string="Issued Visa Document")
    enjaz_doc = fields.Binary(string="Enjaz Document")
    enjaz_ref = fields.Char(string="Ref No")
    enjaz_doc_file_name = fields.Char(string="Enjaz Document")
    enjaz_payment_doc = fields.Binary(string="Payment Confirmation Document")
    enjaz_payment_doc_ref = fields.Char(string="Ref No")
    enjaz_payment_doc_file_name = fields.Char(string="Enjaz Payment Document")
    ewakala_payment_doc = fields.Binary(string="Payment Confirmation Document")
    ewakala_payment_doc_ref = fields.Char(string="Ref No")
    ewakala_payment_doc_file_name = fields.Char(string="Ewakala Payment Document")
    upload_ewakala_doc = fields.Binary(string="COC E-Wakala Document")
    ewakala_ref = fields.Char(string="Ref No")
    ewakala_doc_file_name = fields.Char(string="E-Wakala Document")
    cancelled_ewakala_doc = fields.Binary(string="Cancellation E-Wakala Document")
    cancelled_ewakala_doc_ref = fields.Char(string="Ref No")
    cancelled_ewakala_doc_file_name = fields.Char(string="Cancelled E-Wakala Document")
    cancelled_coc_doc = fields.Binary(string="Cancellation Coc Document")
    cancelled_coc_doc_ref = fields.Char(string="Ref No")
    cancelled_coc_doc_file_name = fields.Char(string="Cancelled Coc Document")
    ewakala_doc_uploaded = fields.Boolean(string="Document Uploaded", default=False, copy=False,store=True)

    @api.depends('enjaz_doc', 'upload_ewakala_doc', 'e_wakala_doc', 'ewakala_payment_doc', 'cancelled_coc_doc','cancelled_ewakala_doc')
    def _compute_ewakala_document_uploaded(self):
        for record in self:
            record.ewakala_doc_uploaded = bool(
            record.enjaz_doc and record.enjaz_payment_doc and record.upload_ewakala_doc and record.ewakala_payment_doc
            or record.cancelled_coc_doc and record.cancelled_ewakala_doc
        )
    ewakala_doc_uploaded = fields.Boolean(compute="_compute_ewakala_document_uploaded", store=True)
    
    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'block_visa_doc' in vals:
            vals['block_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BlockVisaDoc.pdf"
        if 'attached_issued_visa_doc' in vals:
            vals['attached_issued_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttachedIssuedVisaDoc.pdf"
        if 'enjaz_payment_doc' in vals:
            vals['enjaz_payment_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazPaymentDoc.pdf"
        if 'ewakala_payment_doc' in vals:
            vals['ewakala_payment_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EwakalaPaymentDoc.pdf"
        if 'cancelled_e_wakala' in vals:
            vals['cancelled_ewakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancelledEwakalaDoc.pdf"
        if 'cancelled_coc_doc' in vals:
            vals['cancelled_coc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancelledCocDoc.pdf"
        if 'enjaz_doc' in vals:
                vals['enjaz_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazDoc.pdf"
        if 'upload_ewakala_doc' in vals:
                vals['ewakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EWakalaDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'block_visa_doc' in vals:
                vals['block_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BlockVisaDoc.pdf"
            if 'attached_issued_visa_doc' in vals:
                vals['attached_issued_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttachedIssuedVisaDoc.pdf"
            if 'enjaz_payment_doc' in vals:
                vals['enjaz_payment_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazPaymentDoc.pdf"
            if 'ewakala_payment_doc' in vals:
                vals['ewakala_payment_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EwakalaPaymentDoc.pdf"
            if 'cancelled_e_wakala' in vals:
                vals['cancelled_ewakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancelledEwakalaDoc.pdf"
            if 'cancelled_coc_doc' in vals:
                vals['cancelled_coc_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancelledCocDoc.pdf"
            if 'enjaz_doc' in vals:
                vals['enjaz_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazDoc.pdf"
            if 'upload_ewakala_doc' in vals:
                vals['ewakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EWakalaDoc.pdf"
            return super(ServiceEnquiry, self).write(vals)
            
    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'e_wakala':
                if not record.aamalcom_pay and not record.self_pay:
                    raise ValidationError('Please select who needs to pay fees.')
                if record.aamalcom_pay and not (record.billable_to_client or record.billable_to_aamalcom):
                    raise ValidationError('Please select at least one billing detail when Fees to be paid by Aamalcom is selected.')
                if not record.block_visa_doc:
                    raise ValidationError("Kindly Update Block Visa Document")
                if not record.visa_gender:
                    raise ValidationError("Kindly select anyone gender")
                if not record.visa_country_id:
                    raise ValidationError("Kindly select anyone Visa Issuing Country")
                if not record.visa_stamping_city_id:
                    raise ValidationError("Kindly select anyone Visa Stamping City")
                if not record.profession:
                    raise ValidationError("Kindly update profession")
                if not record.visa_religion:
                    raise ValidationError("Kindly select anyone Visa Religion")
                if not record.letter_print_type_id:
                    raise ValidationError("Kindly select anyone type")
                if not record.no_of_visa:
                    raise ValidationError("Kindly update Number of Visa")
                if not record.agency_allocation:
                    raise ValidationError("Kindly update agency allocation name")


            if record.service_request == 'cancelled_e_wakala':
                if not record.attached_issued_visa_doc:
                    raise ValidationError("Kindly Update Issued Visa Document")
                if record.attached_issued_visa_doc and not record.attached_issued_visa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attached Issued Visa Document")
            record.state = 'submitted'  
            record.dynamic_action_status = "PM Needs to assign 1st GE"

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'cancelled_e_wakala':
                if record.cancelled_coc_doc and not record.cancelled_coc_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Cancelled Coc Document")
                if record.cancelled_ewakala_doc and not record.cancelled_ewakala_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Cancelled E-Wakala Document")
            if record.service_request == 'e_wakala':
                if record.enjaz_payment_doc and not record.enjaz_payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Enjaz Payment Document")
                if record.ewakala_payment_doc and not record.ewakala_payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for E-Wakala Payment Document")
                if record.enjaz_doc and not record.enjaz_ref:
                    raise ValidationError("Kindly Update Reference Number for Enjaz Document")
                if record.upload_ewakala_doc and not record.ewakala_ref:
                    raise ValidationError("Kindly Update Reference Number for E-Wakala Document")
        return result    