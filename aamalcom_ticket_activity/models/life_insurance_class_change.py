from odoo import models, fields

class LifeInsuranceClassChange(models.Model):
    _inherit = 'life.insurance.class.change'

    def _schedule_ticket_activity_licc(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_licc_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )


    def action_submit(self):
        result = super(LifeInsuranceClassChange, self).action_submit()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        print("-----------users - insurance employee", users)
        for line in users:
            self._schedule_ticket_activity_licc(
                user_id=line.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )

    def action_submit_to_pm(self):
        result = super(LifeInsuranceClassChange, self).action_submit_to_pm()

        if self.project_manager_id:
            self._schedule_ticket_activity_licc(
                user_id=self.project_manager_id.user_id.id,
                summary='Ticket Ready for PM Review',
                note='Please review the approved request and proceed.'
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

               
