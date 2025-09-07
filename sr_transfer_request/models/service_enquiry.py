from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    to_another_establishment_type = fields.Selection([('local_transfer_to_another_establishment', 'Local Transfer'),('termination_letter_to_another_establishment', 'Termination Request'),('resignation_to_another_establishment', 'Resignation Request')], string="To Another Establishment  Type", store=True)
    np_type = fields.Selection([('np_gov', 'Notice Period as per Government Law'),('np_contract', 'Notice Period as per contract')], string="Notice Period Status", store=True)
    upload_confirmation_doc = fields.Binary(string="Approved LT Request")
    upload_confirmation_doc_file_name = fields.Char(string=" Approved LT Request")

    upload_resignation_doc = fields.Binary(string="Resignation Document")
    upload_resignation_doc_file_name = fields.Char(string="Resignation Document")
    upload_resignation_letter = fields.Binary(string="Resignation Letter")
    upload_resignation_letter_file_name = fields.Char(string="Resignation Letter")
    resignation_doc_ref = fields.Char(string="Ref No.*")
    upload_resignation_qiwa_letter = fields.Binary(string="QIWA Resignation Request")
    upload_resignation_qiwa_letter_file_name = fields.Char(string="QIWA Resignation Request")
    resignation_qiwa_doc_ref = fields.Char(string="Ref No.*")
    upload_signed_qiwa_resignation_letter = fields.Binary(string="Signed QIWA Resignation Request")
    upload_signed_qiwa_resignation_letter_file_name = fields.Char(string="QIWA Resignation Request")
    resignation_signed_qiwa_doc_ref = fields.Char(string="Ref No.*")
    

    type_of_termination = fields. Char(string="Type of Termination")
    articles_for_termination = fields. Char(string="Articles")
    accepted_articles_for_termination = fields. Char(string="Accepted Article")
    last_working_date = fields.Date(string="Last Working Day",store=True)
    last_date = fields.Date(string="Last Working Day",store=True)
    acceptance_date = fields.Date(string="Acceptance Date")

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
    upload_absent_doc = fields.Binary(string="Absent Document")
    upload_absent_doc_file_name = fields.Char(string="Absent Document")
    absent_doc_ref = fields.Char(string="Ref No.*")


    termination_article_short_version = fields.Selection([
        ('article_53', 'Article 53 - Termination During Probationary Period'),
        ('mutual_agreement', 'Article 74 – Mutual Agreement'),
        ('direct_termination', 'Article 80 – Direct Termination'),
        ('non_renewal', 'Article 74 – Non Renewal'),
        ('retirement_age', 'Article 74 – Retirement Age'),
        ('closure_establishment', 'Article 74 - Closure of the Establishment'),
        ('closure_company_activity', 'Article 74 – Closure of Company’s Activity the Employee is Working in'),
        ('inability_to_work', 'Article 79 - Worker\'s Inability to Work'),
        ('without_legitimate_reason', 'Article 77 – Termination without Legitimate Reasons'),
        ('worker_death', 'Article 79 - Worker\'s Death'),
        ('work_injury', 'Article 137 - Worker\'s Inability to Work (Work Injury)'),
    ], string='Termination Article')
    # Fields to be populated automatically based on the selection
    termination_normal_version = fields.Char(string='Termination Article – Details', compute='_compute_termination_details', store=True)
    notice_period = fields.Char(string='Notice period', compute='_compute_termination_details', store=True)
    immediate_termination = fields.Boolean(string='Immediate Termination', compute='_compute_termination_details', store=True)
    grace_period = fields.Char(string='Grace Period', compute='_compute_termination_details', store=True)

    @api.depends('termination_article_short_version')
    def _compute_termination_details(self):
        for record in self:
            record.termination_normal_version = False
            record.notice_period = False
            record.immediate_termination = False
            record.grace_period = False
            
            if record.termination_article_short_version == 'article_53':
                record.termination_normal_version = 'Direct termination of the contract during the probationary period according to Article 53 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'mutual_agreement':
                record.termination_normal_version = 'By mutual agreement according to Article 74 of the Labor Law'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            # Add more elif conditions for the other options from your table
            elif record.termination_article_short_version == 'direct_termination':
                record.termination_normal_version = 'Direct termination of the employment contract by the employer according to Article 80 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'non_renewal':
                record.termination_normal_version = 'Termination of the contract upon its expiration'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'retirement_age':
                record.termination_normal_version = 'The worker reached retirement age according to Article 74 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'closure_establishment':
                record.termination_normal_version = 'Permanent closure of the establishment according to Article 74 of the Labor Law'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'closure_company_activity':
                record.termination_normal_version = 'Termination of the activity in which the worker is employed according to Article 74 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'inability_to_work':
                record.termination_normal_version = 'Worker\'s inability to work according to Article 79 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'without_legitimate_reason':
                record.termination_normal_version = 'Termination of the contract without a legitimate reason according to Article 77 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'worker_death':
                record.termination_normal_version = 'Death of the worker according to Article 79 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = 'No'
            elif record.termination_article_short_version == 'work_injury':
                record.termination_normal_version = 'Worker\'s inability to work (resulting from a work injury) according to Article 137 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'transfer_req' and line.transfer_type == 'to_another_establishment':
                # Validate that to_another_establishment_type is selected
                if not line.to_another_establishment_type:
                    raise ValidationError("Kindly select the To Another Establishment Type")
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'local_transfer_to_another_establishment':
                if not line.upload_confirmation_doc:
                    raise ValidationError("Kindly upload the Approved LT Document for Local Transfer")
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                if not line.upload_confirmation_doc:
                    raise ValidationError("Kindly upload the Approved Termination Document for Termination Request")
                if not line.termination_article_short_version:
                    raise ValidationError("Kindly select anyone  Article for Termination")
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'resignation_to_another_establishment':
                if not line.upload_resignation_doc:
                    raise ValidationError("Kindly upload the Resignation Letter")

    def open_assign_employee_wizard(self):
        """Inherit open_assign_employee_wizard to add validation for visa cancellation"""
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                # Validate required fields for visa cancellation
                # if not line.type_of_termination:
                #     raise ValidationError(_("Please update the type of termination"))
                if not line.last_date:
                    raise ValidationError(_("Please provide the Last Working Date."))
        # Call the parent method
        return super(ServiceEnquiry, self).open_assign_employee_wizard()

    def action_to_another_establishment_termination(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                if line.upload_clearnace_doc and not line.clearance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Clerance Document")
                if line.upload_termination_doc and not line.termination_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Termination Document")
                if line.upload_resignation_qiwa_letter and not line.resignation_qiwa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for QIWA Termination Request")
                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id
    
    def action_to_another_establishment_local(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'local_transfer_to_another_establishment':
                if line.upload_clearnace_doc and not line.clearance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Clerance Document")
           
                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )
    
    def action_to_another_establishment_termination_approval(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                
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
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                # Schedule a new activity for the Operations Manager
                operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )

    def action_doc_upload_pm_termination(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                    if line.upload_signed_qiwa_resignation_letter and not line.resignation_signed_qiwa_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Approved QIWA Termination Document")
                    if line.upload_signed_clerance_doc and not line.signed_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Signed Clerance Document")
                    if line.upload_signed_resignation_doc and not line.signed_resignation_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Signed Termination Document")

                    line.state='submit_for_review'
                    line.dynamic_action_status = f"Document upload Pending by first govt employee"
                    line.action_user_id = line.first_govt_employee_id.user_id.id
                    line.write({'processed_date': fields.Datetime.now()})
                    activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_id.action_feedback(feedback='Approved')
                    
                    # If one user completes the activity or action on the record, delete activities for other users
                    activity_ids = self.env['mail.activity'].search([
                        ('res_id', '=', self.id),
                        ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_ids.unlink()
                    first_govt_employee_id = line.first_govt_employee_id.user_id.id
                    self._schedule_ticket_activity(
                        user_id=first_govt_employee_id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Documents upload) on this ticket.'
                    )

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
                
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                
                # Schedule a new activity for the Operations Manager
                operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )
                
                # Schedule a new activity for the Project Manager on the last working date.
                if line.last_working_date and line.approver_id:
                    line.activity_schedule(
                        act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
                        date_deadline=line.last_working_date,
                        summary='Action Required on Last Working Date',
                        note=f'Action required for PM: Today is the last working date ({line.last_working_date.strftime("%Y-%m-%d")}). Please ensure all necessary actions are completed.',
                        user_id=line.approver_id.user_id.id
                    )

                # Schedule a new activity for the First Government Employee on the last working date.
                if line.last_working_date and line.first_govt_employee_id:
                    line.activity_schedule(
                        act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
                        date_deadline=line.last_working_date,
                        summary='Action Required on Last Working Date',
                        note=f'Action required for First Govt Employee: Today is the last working date ({line.last_working_date.strftime("%Y-%m-%d")}). Please ensure all necessary actions are completed.',
                        user_id=line.first_govt_employee_id.user_id.id
                    )

    def action_to_another_establishment_local_process_complete(self):
        for line in self:
                if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'local_transfer_to_another_establishment':
                    if line.upload_absent_doc and not line.transfer_date:
                        raise ValidationError("Kindly Update Transfer Date")
                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})
                activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()


    def action_to_another_establishment_termination(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'termination_letter_to_another_establishment':
                    if line.upload_clearnace_doc and not line.clearance_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Clerance Document")
                    if line.upload_termination_doc and not line.termination_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Termination Document")
                    if line.upload_resignation_qiwa_letter and not line.resignation_qiwa_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for QIWA Resignation Document")
                    line.state='submit_to_pm'
                    line.dynamic_action_status = "PM needs to review"
                    line.action_user_id=line.approver_id.user_id.id
                    line.write({'processed_date': fields.Datetime.now()})
                    activity_id = self.env['mail.activity'].search([
                        ('res_id', '=', self.id),
                        ('user_id', '=', self.env.user.id),
                        ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_id.action_feedback(feedback='Approved')
                    # If one user completes the activity or action on the record, delete activities for other users
                    activity_ids = self.env['mail.activity'].search([
                        ('res_id', '=', self.id),
                        ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_ids.unlink()
                    client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                    self._schedule_ticket_activity(
                        user_id=client_manager_user_id,
                        summary='Action Required on Ticket',
                        note='Do review and take action on this ticket.'
                    )

    def action_to_another_establishment_accepted_termination(self):
        for line in self:
            if line.service_request == 'transfer_req':
                line.state='submit_for_review'
                line.dynamic_action_status = "First Govt Employee needs to review"
                line.action_user_id=line.first_govt_employee_id.user_id.id
                line.write({'processed_date': fields.Datetime.now()})
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                )

    def action_to_another_establishment_termination_process_complete(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if line.upload_notice_period_confirmation_doc and not line.np_period_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Notice Period document")
                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})
                activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()

    def action_to_another_establishment_resignation(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'resignation_to_another_establishment':
                if  not line.upload_resignation_letter:
                    raise ValidationError("Kindly Update Resignation Letter")
                if line.upload_clearnace_doc and not line.clearance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Clerance Document")
                if not line.resignation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Resignation Letter")

                line.state='submit_to_pm'
                line.dynamic_action_status = "PM needs to review"
                line.action_user_id=line.approver_id.user_id.id
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )
                

    def action_to_another_establishment_resignation_approval(self):
        for line in self:
            if line.service_request == 'transfer_req':
                if not line.signed_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Signed Clerance Document")
                if not line.signed_resignation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Signed Resignation Document")
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
                activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                # Schedule a new activity for the responsible users
                operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )

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
                activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                # Schedule a new activity for the responsible users
                operations_manager_users = self.env.ref('visa_process.group_service_request_hr_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )
    
    def action_approve_by_hr_resignation(self):
        for record in self:
            if record.service_request == 'transfer_req':
                record.state = 'approved'
                record.dynamic_action_status='Documents Uploaded Pending by first govt employee'
                record.action_user_id=record.first_govt_employee_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = record.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                )

    def action_confirmation_pending(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'local_transfer_to_another_establishment':
                if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                    raise ValidationError("Kindly Update Reference Number for Transfer Acceptance Document")
                if not line.acceptance_date:
                    raise ValidationError("Kindly specify the Acceptance Date")

                line.state = 'confirmation_pending'
                line.dynamic_action_status = "Ticket needs to be closed on Last Working Date"
                line.write({'processed_date': fields.Datetime.now()})

                # Get a list of users to notify
                users_to_notify = []
                if line.first_govt_employee_id and line.first_govt_employee_id.user_id:
                    users_to_notify.append(line.first_govt_employee_id.user_id.id)
                if self.env.user.company_spoc_id and self.env.user.company_spoc_id.user_id:
                    users_to_notify.append(self.env.user.company_spoc_id.user_id.id)

                # Schedule one activity for each user on the acceptance date
                for user_id in users_to_notify:
                    line.activity_schedule(
                        act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
                        date_deadline=line.acceptance_date,
                        summary='Last Working Date for Transfer Request',
                        note=f'Action required: Today is the transfer date ({line.acceptance_date.strftime("%Y-%m-%d")}). Please ensure all necessary actions are completed for this transfer request.',
                        user_id=user_id
                    )

                # To avoid duplicates, remove any existing activities on the record.
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'service.enquiry'),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ('user_id', '=', self.env.user.id),
                    ('summary', 'not in', ['Last Working Date for Transfer Request', 'Action Required on Ticket']),
                ])
                activity_ids.unlink()

    def action_to_another_establishment_resignation_process_complete(self):
        for line in self:
            if line.service_request == 'transfer_req' and line.to_another_establishment_type == 'resignation_to_another_establishment':
                if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                    raise ValidationError("Kindly Update Reference Number for Acceptance Document")

                line.state='done'
                line.dynamic_action_status = "Process Completed"
                line.action_user_id=False
                line.write({'processed_date': fields.Datetime.now()})
                activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()

