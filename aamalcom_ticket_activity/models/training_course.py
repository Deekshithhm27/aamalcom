from odoo import models, fields, api

class TrainingCourse(models.Model):
    _inherit = 'training.course'


    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submit(self):
        result = super(TrainingCourse, self).action_submit()
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
            users = self.env.ref('aamalcom_training.group_training_user').users
            for user in users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='A new TrainingCourse has been organised',
                    note='A new Training Program has been organised. Please review and take action.'
                    )
        return result