from odoo import models, fields

class LifeInsuranceClassChange(models.Model):
    _inherit = 'life.insurance.class.change'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )


    def action_submit(self):
        result = super(LifeInsuranceClassChange, self).action_submit()
        insurance_users = self.env.ref('visa_process.group_service_request_insurance_employee').users
        for user in insurance_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action  on this ticket.'
                )
        return result

    def action_submit_to_pm(self):
        result = super(LifeInsuranceClassChange, self).action_submit_to_pm()
        for line in self:
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id

            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()

            if client_manager_user_id:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                )
        return result

        

    def action_done(self):
        result=super(LifeInsuranceClassChange, self).action_done()
        for line in self:
            # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
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
               

               
