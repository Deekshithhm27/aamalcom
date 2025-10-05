from odoo import models, fields

class EndOfService(models.Model):
    _inherit = 'eos.request'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    def action_submitted(self):
        result = super(EndOfService, self).action_confirmed_by_pm()
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
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    def action_submit_to_payroll(self):
        result=super(EndOfService, self).action_submit_to_payroll()
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
            payroll_manager_users = self.env.ref('visa_process.group_service_request_payroll_manager').users
            for user in payroll_manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Service Request',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    def action_confirmed_by_payroll(self):
        result = super(EndOfService, self).action_confirmed_by_payroll()
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
            manager_employee_users = self.env.ref('visa_process.group_service_request_manager').users
            for user in manager_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    def action_send_to_pm(self):
        result = super(EndOfService, self).action_send_to_pm()
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
            pm_users = self.env.ref('visa_process.group_service_request_manager').users
            for user in pm_users:
                self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on End of Service',
                note='A EndOfService requires your action. Please review and take action.'
                )
        return result
    

    def action_confirmed_by_pm(self):
        result = super(EndOfService, self).action_confirmed_by_pm()
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
            hr_employee_users = self.env.ref('visa_process.group_service_request_hr_manager').users
            for user in hr_employee_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result


    def action_send_to_hr_manager(self):
        result = super(EndOfService, self).action_send_to_hr_manager()
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
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    def action_confirmed_by_hr_manager(self):
        result = super(EndOfService, self).action_confirmed_by_hr_manager()
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
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    def action_confirmed_by_gm(self):
        result = super(EndOfService, self).action_confirmed_by_gm()
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
            manager_users = self.env.ref('visa_process.group_service_request_manager').users
            for user in manager_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on End of Service',
                    note='A EndOfService requires your action. Please review and take action.'
                    )
        return result

    
    def action_process_done(self):
        result = super(EndOfService, self).action_process_done()
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



