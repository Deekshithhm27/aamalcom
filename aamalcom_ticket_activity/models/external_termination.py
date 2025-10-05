from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class TerminationService(models.Model):
    _inherit = "termination.request"

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submitted(self):
        result = super(TerminationService, self).action_submitted()
        for line in self:
            # Mark existing activity as done
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Delete other pending activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()

            # Notify company SPOC user
            client_manager_user = self.env.user.company_spoc_id.user_id
            if client_manager_user:
                line._schedule_ticket_activity(
                    user_id=client_manager_user.id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )

        return result


    def action_submit_to_pm(self):
        result=super(TerminationService, self).action_submit_to_payroll()
        for line in self:
            # Mark existing activity as done
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Delete other pending activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()

            # Notify company SPOC user
            client_manager_user = self.env.user.company_spoc_id.user_id
            if client_manager_user:
                line._schedule_ticket_activity(
                    user_id=client_manager_user.id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )

        return result
    
    def action_approved_by_pm(self):
        result=super(TerminationService, self).action_approved_by_pm()
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
                    summary='Action Required on TerminationService',
                    note='A TerminationService requires your action. Please review and take action.'
                    )
        return result
    
    def action_final_review_by_pm(self):
        result=super(TerminationService, self).action_final_review_by_pm()
        for line in self:
            # Mark existing activity as done
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Delete other pending activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()

            # Notify company SPOC user
            client_manager_user = self.env.user.company_spoc_id.user_id
            if client_manager_user:
                line._schedule_ticket_activity(
                    user_id=client_manager_user.id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )

        return result
    
    def action_process_done(self):
        result=super(TerminationService, self).action_process_done()
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