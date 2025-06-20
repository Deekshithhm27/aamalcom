from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('swapping_border_to_iqama', 'Swapping from border to Iqama Number')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'swapping_border_to_iqama': 'cascade'}
    )

    swapping_type = fields.Selection([('employee', 'Employee'),('employee_dependent', 'Employee Dependent')], string="Swapping of Border Number Type", store=True)
    upload_cchi_doc=fields.Binary(string="Upload CCHI Confiramtion Document")
    upload_cchi_doc_file_name=fields.Char(string="Issued Visa Document")
    cchi_doc_ref=fields.Char(string="Ref No.*")
    upload_digital_doc=fields.Binary(string="Upload Digital Iqama Document")
    upload_digital_doc_file_name=fields.Char(string="Digital Document")
    digital_doc_ref=fields.Char(string="Ref No.*")

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'swapping_border_to_iqama':
                if not line.swapping_type:
                    raise ValidationError("Please select at least one: Either Employee or Employee Dependent.")
                line.dynamic_action_status = f"Documents Need to be uploaded by Insurance Dept"
                line.state='submitted_to_insurance'

    def action_submit_swapping(self):
        for line in self:
            if line.service_request == 'swapping_border_to_iqama':
                if line.upload_cchi_doc and not line.cchi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for CCHI Document")
                line.dynamic_action_status=f"Documents Uploaded by Insurance Department, Pm needs to close the ticket"
                line.state='submit_to_pm'

    def action_process_complete_swapping(self):
        for line in self:
            if line.service_request == 'swapping_border_to_iqama':
                line.dynamic_action_status=f"Process Completed"
                line.action_user_id=False
                line.state='done'
    
    def action_submit_swapping_dependents(self):
        for line in self:
            if line.service_request == 'swapping_border_to_iqama':
                if line.upload_cchi_doc and not line.cchi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for CCHI Document")
                if line.upload_digital_doc and not line.digital_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Digital Document")
                line.dynamic_action_status=f"Documents Uploaded by Insurance Department, Pm needs to close the ticket"
                line.state='submit_to_pm'

    def action_process_complete_swapping_dependents(self):
        for line in self:
            if line.service_request == 'swapping_border_to_iqama':
                line.dynamic_action_status=f"Process Completed"
                line.action_user_id=False
                line.state='done'