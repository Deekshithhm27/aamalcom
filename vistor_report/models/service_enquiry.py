from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"
    service_request = fields.Selection(
        selection_add=[
            ('visitor_report', 'Visitor Report')
        ],
        string="Service Requests",
        store=True,
        copy=False
    )
    upload_visitor_report_doc = fields.Binary(string="Upload Visitor Report")
    upload_visitor_report_doc_file_name = fields.Char(string="Visitor Report")
    visitor_report_doc_ref = fields.Char(string="Ref No.*")
    
    muqeem_points = fields.Integer(string="Points")

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'

        if 'upload_visitor_report_doc' in vals:
            vals['upload_visitor_report_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisitorReport.pdf"
        if 'fee_receipt_doc' in vals:
            vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"

        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'

            if 'upload_visitor_report_doc' in vals:
                vals['upload_visitor_report_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_VisitorReport.pdf"
            if 'fee_receipt_doc' in vals:
                vals['fee_receipt_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FeeReceipt.pdf"

        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
       
    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'visitor_report':
                if record.upload_visitor_report_doc and not record.visitor_report_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Visitor Report Doc")
                if record.fee_receipt_doc and not record.fee_receipt_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Fee Receipt Doc")

    