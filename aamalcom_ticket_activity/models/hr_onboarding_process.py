from odoo import models, fields

class HrOnboardingProcess(models.Model):
    _inherit = 'hr.onboarding.process'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit(self):
        result = super(HrOnboardingProcess, self).action_submit()
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
            it_employee_users = self.env.ref('visa_process.group_service_request_it_employee').users
            for user in it_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on Onboarding process',
                    note='A Onboarding Process requires your action. Please review and take action.'
                    )
            return result

    def action_issued(self):
        result = super(HrOnboardingProcess, self).action_issued()
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