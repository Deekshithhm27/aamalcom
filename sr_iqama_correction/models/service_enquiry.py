from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
           ('iqama_correction', 'Iqama Correction')
        ],
        string="Service Requests",
        store=True,
        copy=False
    )

    type_of_request = fields.Char(string="Type of Request")
    attached_doc = fields.Binary(string="Attachment Document")
    upload_correction_doc = fields.Binary(string="Upload Correction Document")
    upload_correction_doc_file_name = fields.Char(string="Correction Document")
    correction_doc_ref = fields.Char(string="Ref No.*")
    upload_muqeem_points_doc = fields.Binary(string="Upload Muqeem Points Document")
    upload_muqeem_points_file_name = fields.Char(string="Muqeem Document")
    muqeem_points_ref = fields.Char(string="Ref No.*")

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for record in self:
            if record.service_request == 'iqama_correction':
                if not record.type_of_request:
                    raise ValidationError("Kindly update the Type of Request.")

    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_muqeem_points_doc' in vals:
            vals['upload_muqeem_points_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
        if 'upload_correction_doc' in vals:
            vals['upload_correction_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CorrectionDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_muqeem_points_doc' in vals:
                vals['upload_muqeem_points_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
            if 'upload_correction_doc' in vals:
                vals['upload_correction_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPointsDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'iqama_correction':
                if record.upload_muqeem_points_doc and not record.muqeem_points_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Doc")
                if record.upload_correction_doc and not record.correction_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Correction Doc")
                if record.upload_muqeem_doc and not record.muqeem_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Points Document")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
        return result
      