from odoo import models, fields


class LocalTransfer(models.Model):
    _inherit = 'local.transfer'

    def _schedule_local_transfer_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_local_transfer_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit(self):
        result = super(LocalTransfer, self).action_submit()
        for line in self:
            client_manager_user_id = line.env.user.company_spoc_id.user_id.id
            self._schedule_local_transfer_activity(
                user_id=client_manager_user_id,
                summary='Action Required On Local Transfer Services',
                note=f'Do review and take action (Approval/ Rejection) on local transfer: {line.name}'
            )
        return result

    def action_approve(self):
        result = super(LocalTransfer, self).action_approve()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_local_transfer_action').id),
        ])
        activity_id.action_feedback(feedback='Approved')
        # If one user completes the activity or action on the record, delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_local_transfer_action').id),
        ])
        activity_ids.unlink()
        return result

    def action_reject(self):
        result = super(LocalTransfer, self).action_reject()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_local_transfer_action').id),
        ])
        activity_id.action_feedback(feedback='Rejected')
        # If one user completes the activity or action on the record, delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_local_transfer_action').id),
        ])
        activity_ids.unlink()
        return result
