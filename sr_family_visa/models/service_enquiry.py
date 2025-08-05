from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
        ('family_visit_visa','Family Visit Visa')
        ],
        string="Service Request",
        store=True,
        copy=False,
        ondelete={
            'family_visit_visa': 'cascade'
        }
    )

    
    doc_uploaded= fields.Boolean(string="Document uploaded",default=False,copy=False)
    
    upload_visit_visa_app_doc = fields.Binary(string="Family application")
    upload_visit_visa_app_doc_file_name = fields.Char(string="Family application")
    upload_family_visa_doc = fields.Binary(string="Family Visit Visa Doc")
    upload_family_visa_doc_file_name = fields.Char(string="Family Visit Visa Doc")
    family_visa_doc_ref = fields.Char(string="Ref No.*")
    upload_family_visit_visa_doc = fields.Binary(string="Family Visit Visa Doc")
    upload_family_visit_visa_doc_file_name = fields.Char(string="Family Visit Visa Doc")
    family_visit_visa_doc_ref = fields.Char(string="Ref No.*")
    family_visa_doc_uploaded = fields.Boolean(string="Document Uploaded", default=False, copy=False,store=True)

    @api.depends('fee_receipt_doc',  'upload_family_visit_visa_doc','upload_family_visa_doc')
    def _compute_family_visa_document_uploaded(self):
        for record in self:
            record.family_visa_doc_uploaded = bool(
            record.upload_family_visa_doc and record.fee_receipt_doc
          
        )

    family_visa_doc_uploaded = fields.Boolean(compute="_compute_family_visa_document_uploaded", store=True)

    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'fee_receipt_doc' in vals:
            vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"
        if 'upload_family_visit_visa_doc' in vals:
            vals['upload_family_visit_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf"
        if 'upload_family_visa_doc' in vals:
            vals['upload_family_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf"
        if 'upload_visit_visa_app_doc' in vals:
            vals['upload_visit_visa_app_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyApplicationDoc.pdf"        
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'fee_receipt_doc' in vals:
                vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"
            if 'upload_family_visit_visa_doc' in vals:
                vals['upload_family_visit_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf" 
            if 'upload_family_visa_doc' in vals:
                vals['upload_family_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisitVisaDoc.pdf"
            if 'upload_visit_visa_app_doc' in vals:
                vals['upload_visit_visa_app_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyApplicationDoc.pdf"       
        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()

    def action_submit_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for record in self:
            if record.service_request == 'family_visit_visa':
                if record.upload_payment_doc and not record.payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number For Payment Confirmation Document")
                record.dynamic_action_status = 'Payment done by client spoc. Documents upload pending by first employee'
                record.action_user_id = record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})
        return result

       

    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'family_visit_visa':
                if record.upload_family_visit_visa_doc and not record.family_visit_visa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Family visit visa") 
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt")     

    