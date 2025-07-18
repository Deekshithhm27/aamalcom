from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('final_clearance', 'Final Clearance')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'final_clearance': 'cascade'}
    )

    final_clearance_type = fields.Selection([('final_clearance_local_transfer', 'Local Transfer'),('final_clearance_final_exit', 'Final Exit')], string="Type of Service", store=True)
    upload_clearance_doc = fields.Binary(string="Upload Clearance Document")
    upload_clearance_doc_file_name = fields.Char(string="Clearance Document")
    clearance_doc_ref = fields.Char(string="Ref No.*")
    signed_clearance_doc = fields.Binary(string="Signed Clearance Document")
    signed_clearance_doc_ref = fields.Char(string="Ref No")
    signed_clearance_doc_file_name = fields.Char(string="Signed Document")
    upload_final_acceptance = fields.Binary(string="Final Acceptance Document")
    final_acceptance_doc_ref = fields.Char(string="Ref No")
    final_acceptance_doc_file_name = fields.Char(string="Final Acceptance Document")
    upload_signed_doc = fields.Binary(string="Clearance Signed Document")
    upload_signed_doc_ref = fields.Char(string="Ref No")
    upload_signed_doc_file_name = fields.Char(string="Clearance Signed Document")

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_clearance_doc' in vals:
            vals['upload_clearance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ClearanceDoc.pdf"
        if 'signed_clearance_doc' in vals:
            vals['signed_clearance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SignedClearanceDoc.pdf"
        if 'upload_final_acceptance' in vals:
            vals['final_acceptance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FinalAcceptanceDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_clearance_doc' in vals:
                vals['upload_clearance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ClearanceDoc.pdf"
            if 'upload_signed_doc' in vals:
                vals['upload_signed_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SignedDoc.pdf"
            if 'upload_final_acceptance' in vals:
                vals['final_acceptance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FinalAcceptanceDoc.pdf"
        return super(ServiceEnquiry, self).write(vals) 


    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'final_clearance' :
                if not line.final_clearance_type:
                    raise ValidationError("Please select at least one: Local Transfer or Final Exit")
            
    def action_first_govt_emp_submit(self):
        for record in self:
            if record.service_request == 'final_clearance':
                if record.upload_clearance_doc and not record.clearance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Clearance Doc")
                record.state = 'doc_uploaded_by_first_govt_employee'
                record.dynamic_action_status = "Documents Uploaded by first govt employee. Second govt employee need to be assigned by PM"
                record.action_user_id=record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})
                
    def open_assign_employee_wizard(self):
        """ super method to add a new condition for `exit_reentry_issuance_ext` service request. """
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for record in self:
            if record.service_request == 'salary_increase_process' and record.state == 'doc_uploaded_by_first_govt_employee':
                # level = 'level1'
                department_ids = []
                req_lines = record.service_request_config_id.service_department_lines
                sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
                for lines in sorted_lines:
                    # if level == 'level1':
                    department_ids.append((4, lines.department_id.id))

                result.update({
                    'name': 'Select Employee',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.selection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_department_ids': department_ids,
                        'default_assign_type': 'assign',
                        'default_levels': 'level2',
                    },
                })
        return result

    def action_submit_to_hr(self):
        for record in self:
            if record.service_request == 'final_clearance':
                record.state = 'waiting_hr_approval'
                record.dynamic_action_status = "Waiting for Approval by HR"
                group = self.env.ref('visa_process.group_service_request_payroll_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.action_user_id = employee.user_id
                record.write({'processed_date': fields.Datetime.now()})
    
    def action_approve_by_hr(self):
        for record in self:
            if record.service_request == 'final_clearance':
                record.state = 'approved'
                record.dynamic_action_status='Documents Uploaded Pending by second govt employee'
                record.action_user_id=record.second_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})


    def action_process_complete_final_clearance(self):
        for record in self:
            if record.service_request == 'final_clearance':
                if record.upload_final_acceptance and not record.final_acceptance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Final Doc")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
                record.write({'processed_date': fields.Datetime.now()})
        

           

