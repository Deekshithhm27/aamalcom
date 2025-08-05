from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    to_another_establishment_type = fields.Selection([('local_transfer_to_another_establishment', 'Local Transfer'),('termination_letter_to_another_establishment', 'Termination Request'),('resignation_to_another_establishment', 'Resignation Request')], string="To Another Establishment  Type", store=True)
    np_type = fields.Selection([('np_gov', 'Notice Period as per Government Law'),('np_contract', 'Notice Period as per contract')], string="Notice Period Status", store=True)
    upload_confirmation_doc = fields.Binary(string="Confirmation Document")
    upload_confirmation_doc_file_name = fields.Char(string="Confirmation Document")
    upload_resignation_doc = fields.Binary(string="Resignation Document")
    upload_resignation_doc_file_name = fields.Char(string="Resignation Document")
    upload_resignation_letter = fields.Binary(string="Resignation Letter")
    upload_resignation_letter_file_name = fields.Char(string="Resignation Letter")
    resignation_doc_ref = fields.Char(string="Ref No.*")
    type_of_termination = fields. Char(string="Type of Termination")
    articles_for_termination = fields. Char(string="Articles")
    accepted_articles_for_termination = fields. Char(string="Accepted Article")
    last_working_date = fields.Date(string="Last Working Day")
    transfer_date = fields.Date(string="Transfer Date")
    notice_period_date = fields.Date(string="Notice Period")
    upload_clearnace_doc = fields.Binary(string="Clearance Document")
    upload_clearnace_doc_file_name = fields.Char(string="Clearance Document")
    clearance_doc_ref = fields.Char(string="Ref No.*")
    upload_termination_doc = fields.Binary(string="Termination Document")
    upload_termination_doc_file_name = fields.Char(string="Termination Document")
    termination_doc_ref = fields.Char(string="Ref No.*")
    upload_signed_doc = fields.Binary(string="Signed Document")
    upload_signed_doc_file_name = fields.Char(string="Signed Document")
    signed_doc_ref = fields.Char(string="Ref No.*")
    upload_signed_clerance_doc = fields.Binary(string="Signed Clearance Document")
    upload_signed_clerance_doc_file_name = fields.Char(string="Signed Clearance Document")
    signed_clearance_doc_ref = fields.Char(string="Ref No.*")
    upload_signed_resignation_doc = fields.Binary(string="Signed Resignation Document")
    upload_signed_resignation_doc_file_name = fields.Char(string="Signed Resignation Document")
    signed_resignation_doc_ref = fields.Char(string="Ref No.*")
    upload_notice_period_confirmation_doc = fields.Binary(string="Confirmation Document")
    upload_notice_period_confirmation_doc_file_name = fields.Char(string="Confirmation Document")
    np_period_doc_ref = fields.Char(string="Ref No.*")

    def action_to_another_establishment_local(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if line.upload_clearnace_doc and not line.clearance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Clerance Document")
                if line.upload_termination_doc and not line.termination_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Termination Document")
                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id

    def action_to_another_establishment_local_approval(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if not line.signed_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Signed Document")
                if not line.last_working_date:
                    raise ValidationError("Kindly Update Last Working Date")
                line.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                line.dynamic_action_status = f"Waiting for approval by OM"
                line.action_user_id = employee.user_id
                line.write({'processed_date': fields.Datetime.now()})
                self.send_email_to_op()

    def action_to_another_establishment_local_process_complete(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                    raise ValidationError("Kindly Update Reference Number for Transfer Acceptance Document")
                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})

    def action_to_another_establishment_termination(self):
        for line in self:
            if line.service_request == 'transfer_req':
                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id

    def action_to_another_establishment_accepted_termination(self):
        for line in self:
            if line.service_request == 'transfer_req':
                line.state='submit_for_review'
                line.dynamic_action_status = "First Govt Employee needs to review"
                line.action_user_id=line.first_govt_employee_id.user_id.id

    def action_to_another_establishment_termination_process_complete(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if line.upload_termination_doc and not line.termination_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Termination document")
                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})

    def action_to_another_establishment_resignation(self):
        for line in self:
            if line.service_request == 'transfer_req':
                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id

    def action_to_another_establishment_resignation_approval(self):
        for line in self:
            if line.service_request == 'transfer_req':
                # if not line.signed_clearance_doc_ref:
                #     raise ValidationError("Kindly Update Reference Number for Signed Clerance Document")
                # if not line.signed_resignation_doc_ref:
                #     raise ValidationError("Kindly Update Reference Number for Signed Resignation Document")
                line.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                line.dynamic_action_status = f"Waiting for approval by OM"
                line.action_user_id = employee.user_id
                line.write({'processed_date': fields.Datetime.now()})
                self.send_email_to_op()

    def action_submit_to_hr_resignation(self):
        for record in self:
            if record.service_request == 'transfer_req':
                record.state = 'waiting_hr_approval'
                record.dynamic_action_status = "Waiting for Approval by HR"
                group = self.env.ref('visa_process.group_service_request_payroll_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.action_user_id = employee.user_id
                record.write({'processed_date': fields.Datetime.now()})
    
    def action_approve_by_hr_resignation(self):
        for record in self:
            if record.service_request == 'transfer_req':
                record.state = 'approved'
                record.dynamic_action_status='Documents Uploaded Pending by first govt employee'
                record.action_user_id=record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_to_another_establishment_resignation_process_complete(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                    raise ValidationError("Kindly Update Reference Number for Transfer Acceptance Document")
                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})

