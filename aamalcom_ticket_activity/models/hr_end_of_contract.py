from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class EndofContract(models.Model):
    _inherit = "hr.end.of.contract"

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submit_end_of_contract(self):
        result=super(EndofContract, self).action_submit_end_of_contract()
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
            coach = line.employee_id.coach_id
            if coach and coach.user_id:
                # Notify coach
                line._schedule_ticket_activity(
                    user_id=coach.user_id.id,
                    summary="End of Contract Submitted",
                    note=f"End of Contract has been submitted for {line.employee_id.name}. Please review."
                )
        return result

    def action_submit_by_dept_head(self):
        result = super(EndofContract, self).action_submit_by_dept_head()
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
            hr_employee_users = self.env.ref('visa_process.group_service_request_hr_employee').users
            for user in hr_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Contract',
                    note='A EndofContract requires your action. Please review and take action.'
                    )
        return result
    
    def action_approve_by_dept_head(self):
        result = super(EndofContract, self).action_approve_by_dept_head()
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
            hr_employee_users = self.env.ref('visa_process.group_service_request_hr_employee').users
            for user in hr_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Contract',
                    note='A EndofContract requires your action. Please review and take action.'
                    )
        return result

    def action_process_complete_end_of_contract(self):
        result=super(EndofContract, self).action_process_complete_end_of_contract()
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
