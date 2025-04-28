from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[('general_query','General Query')],
        string="Service Requests",
        store=True,
        copy=False,ondelete={'general_query': 'cascade'}
    )

    upload_doc = fields.Binary(string="Upload Attached Document")
    upload_doc_file_name = fields.Char(string="Document")
    doc_ref = fields.Char(string="Ref No.*")

    def open_assign_employee_wizard(self):
        """ Extend the original method to add 'general_query' condition. """

        # Call the original method first
        res = super(ServiceEnquiry, self).open_assign_employee_wizard()

        for line in self:
            if line.service_request == 'general_query':
                all_departments = self.env['hr.department'].search([]).ids  # Get all department IDs
                department_ids = [(4, dept_id) for dept_id in all_departments]
                
                # Modify the context with new department_ids
                res['context'].update({'default_department_ids': department_ids})

        return res

    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'

        if 'upload_doc' in vals:
            vals['upload_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_Document.pdf"
        
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'

            if 'upload_doc' in vals:
                vals['upload_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_Document.pdf"

        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
       
    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'general_query':
                if record.upload_doc and not record.doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attached Doc")
