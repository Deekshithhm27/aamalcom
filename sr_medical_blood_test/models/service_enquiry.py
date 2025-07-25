from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('medical_blood_test', 'Iqama Issuance-Medical Blood Test')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'medical_blood_test': 'cascade'}

    )

    upload_stamped_visa_doc=fields.Binary(string="Stamped Visa Document")
    stamped_visa_doc_ref=fields.Char(string="Ref No.*")
    upload_stamped_visa_doc_file_name=fields.Char(string="Stamped Visa Document")
    upload_medical_test_doc=fields.Binary(string="Medical Test Document")
    medical_test_doc_ref=fields.Char(string="Ref No.*")
    upload_medical_test_doc_file_name=fields.Char(string="Medical Test Document")
    clinic_name = fields.Char(string="Clinic Name")
    total_price = fields.Monetary(string="Price")

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_stamped_visa_doc' in vals:
            vals['upload_stamped_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_StampedVisaDoc.pdf"
        if 'upload_medical_test_doc' in vals:
            vals['upload_medical_test_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MedicalTestDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_stamped_visa_doc' in vals:
                vals['upload_stamped_visa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_StampedVisaDoc.pdf"
            if 'upload_medical_test_doc' in vals:
                vals['upload_medical_test_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MedicalTestDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)  

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'medical_blood_test':
                line.dynamic_action_status = "PM needs to upload document"
                line.action_user_id=line.approver_id.user_id.id

    def action_submit_to_treasury(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for line in self:
        # Check if a treasury record already exists for this service request
            existing_doc = self.env['service.request.treasury'].sudo().search([
            ('service_request_id', '=', line.id)
            ], limit=1)
            if existing_doc:
                continue 
            for line in self:
                vals = {
                'service_request_id': self.id,
                'client_id': self.client_id.id,
                'client_parent_id':self.client_id.parent_id.id,
                'employee_id':self.employee_id.id,
                }
                service_request_treasury_id = self.env['service.request.treasury'].sudo().create(vals)
                if line.service_request == 'medical_blood_test':
                    if line.upload_stamped_visa_doc and not line.stamped_visa_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Stamped Visa Document")
                if service_request_treasury_id :
                    line.state="passed_to_treasury"
                    line.dynamic_action_status = "Submitted to the Treasury Department by PM,Review is pending by Treasury"
                    finance_manager = self.env['hr.department'].search([('name', 'ilike', 'Finance')], limit=1).manager_id
                    line.action_user_id = finance_manager.user_id


    def open_assign_employee_wizard(self):
        """ super method to add a new condition for `exit_reentry_issuance_ext` service request. """
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for record in self:
            if record.service_request == 'medical_blood_test' and record.state == 'approved':
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
                        'default_levels': 'level1',
                    },
                })
        return result

    def action_finance_submit_to_treasury(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for record in self:
            if record.service_request == 'medical_blood_test':
                record.state = 'approved'
                record.dynamic_action_status = "Review to be done by Treasury Department"
                record.gm_approver_id = current_employee
                finance_manager = self.env['hr.department'].search([('name', 'ilike', 'Finance')], limit=1).manager_id
                record.action_user_id = finance_manager.user_id
                treasury_record = self.env['service.request.treasury'].sudo().search([
                    ('service_request_id', '=', record.id)
                ], limit=1) # Use limit=1 as there should be only one treasury record per service request
                if treasury_record:
                    treasury_record.write({'state': 'submitted'})
                else:
                    # Handle the case where a treasury record might not exist yet.
                    # This might happen if 'action_submit_to_treasury' wasn't called first.
                    # You might want to create it here or raise a warning.
                    # For now, let's create it if it doesn't exist, mirroring action_submit_to_treasury's creation logic.
                    vals = {
                        'service_request_id': record.id,
                        'client_id': record.client_id.id,
                        'client_parent_id': record.client_id.parent_id.id,
                        'employee_id': record.employee_id.id,
                        'state': 'submitted_to_treasury', # Set state directly upon creation
                    }
                    self.env['service.request.treasury'].sudo().create(vals)



    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'medical_blood_test':
                if record.upload_medical_test_doc and not record.medical_test_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Medical Test Doc")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
        return result

          