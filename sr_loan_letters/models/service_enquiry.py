

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('bank_loan', 'Bank Loan Letter')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'bank_loan': 'cascade'}
    )

    upload_bank_loan_doc = fields.Binary(string="Bank Loan Document")
    upload_bank_loan_doc_file_name = fields.Char(string="Bank Loan Document")
    bank_loan_doc_ref = fields.Char(string="Ref No.*")
    upload_fee_receipt_doc = fields.Binary(string="Fee Receipt Document")
    upload_fee_receipt_doc_file_name = fields.Char(string="Fee Receipt Document")
    fee_receipt_doc_ref = fields.Char(string="Ref No.*")
    doc_uploaded = fields.Boolean(string="Document uploaded",default=False,copy=False)

    @api.onchange('upload_bank_loan_doc', 'upload_fee_receipt_doc')
    def loan_letter_document_uploaded(self):
        for record in self:
            if record.service_request == 'bank_loan' and record.upload_bank_loan_doc and record.upload_fee_receipt_doc:
                record.doc_uploaded = False  

    
        
    

    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'

        if 'upload_bank_loan_doc' in vals:
            vals['upload_bank_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLoanLetter.pdf"
        if 'upload_fee_receipt_doc' in vals:
            vals['upload_fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"

        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'

            if 'upload_bank_loan_doc' in vals:
                vals['upload_bank_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLoanLetter.pdf"
            if 'upload_fee_receipt_doc' in vals:
                vals['upload_fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"

        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
    

    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'bank_loan':
                if record.upload_bank_loan_doc and not record.bank_loan_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank Loan Letter")
                if record.upload_fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt")

    