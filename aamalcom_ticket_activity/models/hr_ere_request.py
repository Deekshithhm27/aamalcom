from odoo import models, fields

class ExitReentryService(models.Model):
    _inherit = 'hr.exit.reentry'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submit_ere(self):
        result = super(ExitReentryService, self).action_approval_dept()
        for line in self:
            hr_manager_users = self.env.ref('visa_process.group_service_request_hr_manager').users
            for user in hr_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on ExitReentryService Request',
                    note='A ExitReentryService Request requires your action. Please review and take action.'
                    )
        return result

    def action_approval_dept(self):
        result = super(ExitReentryService, self).action_approval_dept()
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
                    summary='Action Required on ExitReentryService Request',
                    note='A ExitReentryService Request requires your action. Please review and take action.'
                    )
            return result

    def action_approval_hr(self):
        result = super(ExitReentryService, self).action_approval_hr()
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
                    summary='Action Required on ExitReentryService Request',
                    note='A ExitReentryService Request requires your action. Please review and take action.'
                    )
            return result

    def action_approval_gm(self):
        result = super(ExitReentryService, self).action_approval_gm()
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

        # Schedule a new activity for the responsible users
        fm_users = self.env.ref('visa_process.group_service_request_finance_manager').users
        for user in fm_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action(Approval) on this ticket.'
            )
        return result
    
    def action_approval_fm(self):
        result = super(ExitReentryService, self).action_approval_fm()
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
    
    def action_submit_if_employee(self):
        result = super(ExitReentryService, self).action_submit_if_employee()
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
                    summary='Action Required on ExitReentryService Request',
                    note='A ExitReentryService Request requires your action. Please review and take action.'
                    )
                return result
    
    def action_done_ere(self):
        result = super(ExitReentryService, self).action_done_ere()
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

