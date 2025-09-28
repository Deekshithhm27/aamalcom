from odoo import models, fields

class HRMedicalBloodTest(models.Model):
    _inherit = 'hr.medical.blood.test'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submit_medical(self):
        result = super(HRMedicalBloodTest, self).action_submit_medical()
        for line in self:
            pm_manager_users = self.env.ref('visa_process.group_service_request_manager').users
            for user in pm_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on Iqama Issuance-Medical Report',
                    note='A Iqama Issuance-Medical Report requires your action. Please review and take action.'
                    )
            return result

    def action_submit_to_treasury_hr(self):
        result = super(HRMedicalBloodTest, self).action_submit_to_treasury_hr()
        for line in self:
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
            # Code snippet from your previous message, representing the flawed logic.
            fm_manager_users = self.env.ref('visa_process.group_service_request_finance_manager').users
            for user in fm_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on MedicalBloodTest',
                    note='A MedicalBloodTest requires your action. Please review and take action.'
                    )
            return result
    
    def action_oh_approve(self):
        result = super(HRMedicalBloodTest, self).action_oh_approve()
        for line in self:
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
            # Code snippet from your previous message, representing the flawed logic.
            gm_manager_users = self.env.ref('visa_process.group_service_request_general_manager').users
            for user in gm_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on MedicalBloodTest',
                    note='A MedicalBloodTest requires your action. Please review and take action.'
                    )
            return result

    def action_gm_approve(self):
        result = super(HRMedicalBloodTest, self).action_gm_approve()
        for line in self:
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
            # Code snippet from your previous message, representing the flawed logic.
            fm_manager_users = self.env.ref('visa_process.group_service_request_finance_manager').users
            for user in fm_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on MedicalBloodTest',
                    note='A MedicalBloodTest requires your action. Please review and take action.'
                    )
            return result

    def action_fm_approve(self):
        result = super(HRMedicalBloodTest, self).action_fm_approve()
        for line in self:
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
            # Code snippet from your previous message, representing the flawed logic.
            pm_users = self.env.ref('visa_process.group_service_request_manager').users
            for user in pm_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required (Assign Employee) on MedicalBloodTest',
                    note='A MedicalBloodTest (Assign Employee) requires your action. Please review and take action.'
                    )
            return result
    
    def action_process_complete(self):
        result = super(HRMedicalBloodTest, self).action_process_complete()
        for line in self:
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
        return result
