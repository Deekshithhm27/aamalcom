from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LoanRequest(models.Model):
    """Can create new loan requests and manage records"""
    _inherit = 'loan.request'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_loan_request(self):
        result=super(LoanRequest, self).action_loan_request()
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
                    summary="Air ticket Submitted",
                    note=f"Air ticket has been submitted for {line.employee_id.name}. Please review."
                )
        return result
    def action_loan_approved(self):
        result = super(LoanRequest, self).action_loan_approved()
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
                    summary='Action Required on LoanRequest',
                    note='A LoanRequest requires your action. Please review and take action.'
                    )
            return result

    def action_loan_approved_hr(self):
        result = super(LoanRequest, self).action_loan_approved_hr()
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
            gm_manager_users = self.env.ref('visa_process.group_service_request_general_manager').users
            for user in gm_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on LoanRequest',
                    note='A LoanRequest requires your action. Please review and take action.'
                    )
            return result

    def action_loan_approved_gm(self):
        result = super(LoanRequest, self).action_loan_approved_gm()
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
            fm_employee_users = self.env.ref('visa_process.group_service_request_finance_manager').users
            for user in fm_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on LoanRequest',
                    note='A LoanRequest requires your action. Please review and take action.'
                    )
            return result

    def action_close_loan(self):
        result = super(LoanRequest, self).action_close_loan()
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