from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class LifeInsuranceEnrollment(models.Model):
    _inherit = 'life.insurance.enrollment'

    def _schedule_ticket_activity_lie(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_lie_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )


    def action_submit(self):
        result = super(LifeInsuranceEnrollment, self).action_submit()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        print("-----------users - insurance employee", users)
        for line in users:
            self._schedule_ticket_activity_lie(
                user_id=line.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result 

    def action_confirm_activation(self):
        result = super(LifeInsuranceEnrollment, self).action_confirm_activation()

        if self.project_manager_id:
            self._schedule_ticket_activity_lie(
                user_id=self.project_manager_id.user_id.id,
                summary='Ticket Ready for PM Review',
                note='Please review the approved request and proceed.'
            )
        return result

    def action_done(self):
        result = super(LifeInsuranceEnrollment, self).action_done()
        activity_type_ticket = self.env.ref(
            'aamalcom_ticket_activity.mail_activity_type_ticket_lie_action',
            raise_if_not_found=False
        )

        if activity_type_ticket:
            activities = self.env['mail.activity'].sudo().search([
                ('res_model', '=', 'life.insurance.enrollment'),
                ('res_id', '=', self.id),
                ('activity_type_id', '=', activity_type_ticket.id),
                ('summary', 'in', [
                    'Action Required on Ticket',
                    'Ticket Ready for PM Review'
                ])
            ])
            for activity in activities:
                try:
                    activity.with_user(activity.user_id).action_feedback(
                        feedback='Auto-marked as done after completion.'
                    )
                except Exception as e:
                    _logger.warning(f"Could not mark activity {activity.id} as done: {e}")

        return result