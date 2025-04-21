from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('family_resident','Family Resident Visa Application'),('family_visa_letter','Family Visa Letter'),('istiqdam_form','Istiqdam Form(Family Visa Letter)'),
        ('family_visit_visa','Family Visit Visa')
        ],
        string="Service Request",
        store=True,
        copy=False,
        ondelete={
            'family_resident': 'cascade',
            'family_visa_letter': 'cascade',
            'istiqdam_form': 'cascade',
            'family_visit_visa': 'cascade',
        }
    )

    upload_attested_application_doc = fields.Binary(string="Upload Attested Application")
    upload_attested_application_file_name = fields.Char(string="Attested Application")
    attested_application_doc_ref = fields.Char(string="Ref No.*")
    
    upload_family_visa_letter_doc = fields.Binary(string="Family Visa Letter")
    upload_family_visa_letter_doc_file_name = fields.Char(string="Family Visa Letter")
    family_visa_letter_doc_ref = fields.Char(string="Ref No.*")
    doc_uploaded= fields.Boolean(string="Document uploaded",default=False,copy=False)
    draft_istiqdam = fields.Binary(string="Draft Istiqdam",compute="auto_fill_istiqdam_form",store=True)
    updated_istiqdam_form_doc = fields.Binary(string="Updated Istiqdam Form")
    upload_istiqdam_form_doc_file_name = fields.Char(string="Updated Istiqdam Form")
    upload_istiqdam_form_doc = fields.Binary(string="Upload Istiqdam Form")
    istiqdam_form_doc_ref = fields.Char(string="Ref No.*")
    upload_visit_visa_app_doc = fields.Binary(string="Family application")
    upload_visit_visa_app_doc_file_name = fields.Char(string="Family application")
    
    upload_family_visit_visa_doc = fields.Binary(string="Family Visit Visa Doc")
    upload_family_visit_visa_doc_file_name = fields.Char(string="Family Visit Visa Doc")
    family_visit_visa_doc_ref = fields.Char(string="Ref No.*")
    family_visa_doc_uploaded = fields.Boolean(string="Document Uploaded", default=False, copy=False,store=True)

    @api.depends('upload_family_visa_letter_doc', 'upload_attested_application_doc', 'fee_receipt_doc', 'upload_istiqdam_form_doc', 'upload_family_visit_visa_doc')
    def _compute_family_visa_document_uploaded(self):
        for record in self:
            record.family_visa_doc_uploaded = bool(
            record.upload_attested_application_doc and record.fee_receipt_doc
            or record.upload_istiqdam_form_doc
            or record.upload_family_visit_visa_doc
            or record.upload_family_visa_letter_doc
        )

    family_visa_doc_uploaded = fields.Boolean(compute="_compute_family_visa_document_uploaded", store=True)

    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'

        if 'upload_attested_application_doc' in vals:
            vals['upload_attested_application_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestedApplication.pdf"
        if 'fee_receipt_doc' in vals:
            vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"
        if 'upload_family_visa_letter_doc' in vals:
            vals['upload_family_visa_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisaLetter.pdf"
        if 'upload_istiqdam_form_doc' in vals:
            vals['upload_istiqdam_form_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamForm.pdf"
        if 'upload_family_visit_visa_doc' in vals:
            vals['upload_family_visit_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf"
        if 'upload_visit_visa_app_doc' in vals:
            vals['upload_visit_visa_app_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyApplicationDoc.pdf"        
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'

            if 'upload_attested_application_doc' in vals:
                vals['upload_attested_application_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestedApplication.pdf"
            if 'fee_receipt_doc' in vals:
                vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"
            if 'upload_family_visa_letter_doc' in vals:
                vals['upload_family_visa_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisaLetter.pdf"
            if 'upload_istiqdam_form_doc' in vals:
                vals['upload_istiqdam_form_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamForm.pdf"
            if 'upload_family_visit_visa_doc' in vals:
                vals['upload_family_visit_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf" 
            if 'upload_visit_visa_app_doc' in vals:
                vals['upload_visit_visa_app_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyApplicationDoc.pdf"       
        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()

    @api.depends('service_request')
    def auto_fill_istiqdam_form(self):
        for line in self:
            if line.service_request == 'istiqdam_form':
                istiqdam_id = self.env['visa.ref.documents'].search([('is_istiqdam_doc','=',True)],limit=1)
                line.draft_istiqdam = istiqdam_id.istiqdam_doc
            else:
                line.draft_istiqdam = False     

    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'family_resident':
                if record.upload_attested_application_doc and not record.attested_application_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attested Visa Application")
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt")
            if record.service_request == 'family_visa_letter':
                if record.upload_family_visa_letter_doc and not record.family_visa_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Family visa letter")  
            if record.service_request == 'istiqdam_form':
                if record.upload_istiqdam_form_doc and not record.istiqdam_form_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Istiqdam form")
            if record.service_request == 'family_visit_visa':
                if record.upload_family_visit_visa_doc and not record.family_visit_visa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Family visit visa")      

    