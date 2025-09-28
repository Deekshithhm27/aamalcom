from odoo import models, fields

class HrBusinessTrip(models.Model):
    _inherit = 'hr.business.trip'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit_to_hr(self):
        result = super(HrBusinessTrip, self).action_submit_to_hr()
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
            hr_manager_users = self.env.ref('visa_process.group_service_request_hr_manager').users
            for user in hr_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on BusinessTrip',
                    note='A BusinessTrip requires your action. Please review and take action.'
                    )
            return result

    def action_approved_by_hr(self):
        result = super(HrBusinessTrip, self).action_approved_by_hr()
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
                    summary='Action Required on BusinessTrip',
                    note='A BusinessTrip requires your action. Please review and take action.'
                    )
            return result

    def action_approved_by_fm(self):
        result = super(HrBusinessTrip, self).action_approved_by_fm()
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
            gm_users = self.env.ref('visa_process.group_service_request_general_manager').users
            for user in gm_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on HrBusinessTrip',
                    note='A HrBusinessTrip requires your action. Please review and take action.'
                    )
            return result

    def action_approved_by_gm(self):
        result = super(HrBusinessTrip, self).action_approved_by_gm()
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