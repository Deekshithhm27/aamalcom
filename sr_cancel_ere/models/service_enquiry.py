from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
           ('cancel_ere','Cancel Exit Rentry issuance')
        ],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'cancel_ere': 'cascade'}
    )
    
    service_request_id = fields.Many2one('service.enquiry',order='create_date DESC', )
    remarks_ere = fields.Text(string="Remarks")
    ere_cancellation_doc=fields.Binary(string="Cancellation Document")
    ere_cancellation_doc_file_name=fields.Char(string="Cancellation Document")
    ere_cancellation_doc_ref=fields.Char(string="Ref No.*")

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()

    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'ere_cancellation_doc' in vals:
            vals['ere_cancellation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancellationDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'ere_cancellation_doc' in vals:
                vals['ere_cancellation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CancellationDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'cancel_ere':
                if record.ere_cancellation_doc and not record.ere_cancellation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Cancellation Doc")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
        return result
      