from odoo import models, fields, api

class HrSuspendingEmployee(models.Model):
    _inherit = 'hr.suspending'


    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submit_to_employee(self):
        result = super(HrSuspendingEmployee, self).action_submit_to_employee()
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
            if line.employee_id and line.employee_id.user_id:
                self._schedule_ticket_activity(
                    user_id=line.employee_id.user_id.id,
                    summary='Review suspending letter',
                    note='Your suspending letter has been issued. Please review .'
                )
        return result