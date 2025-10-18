from odoo import models, fields

class ClientPayslipApproval(models.Model):
    _inherit = 'client.payslip.approval'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit_to_payroll(self):
        result=super(ClientPayslipApproval, self).action_submit_to_payroll()
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
                payroll_manager_users = self.env.ref('visa_process.group_service_request_payroll_employee').users
                for user in payroll_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on New Payslip Approval',
                        note='A Payslip Approval requires your action. Please review and take action.'
                        )
        
        return result

    def action_submit_to_pm(self):
        result=super(ClientPayslipApproval, self).action_submit_to_pm()
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
                manager_users = self.env.ref('visa_process.group_service_request_manager').users
                for user in manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on New Payslip Approval',
                        note='A Payslip Approval requires your action. Please review and take action.'
                        )
        
        return result

    def action_verified_by_pm(self):
        result=super(ClientPayslipApproval, self).action_verified_by_pm()
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
                payroll_employee_users = self.env.ref('visa_process.group_service_request_payroll_employee').users
                for user in payroll_employee_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Verified Payroll Approval',
                        note='A Payroll has been verified by PM requires your action.'
                        )
        
        return result

    def action_submit_to_fm_manager(self):
        result=super(ClientPayslipApproval, self).action_submit_to_fm_manager()
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
                finance_manager_users = self.env.ref('visa_process.group_service_request_finance_manager').users
                for user in finance_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on  Payroll Approval',
                        note='A Payroll has been verified by PM and reviewd requires your action.'
                        )
        
        return result

    def action_submit_to_payroll_manager(self):
        result=super(ClientPayslipApproval, self).action_submit_to_payroll_manager()
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
                payroll_manager_users = self.env.ref('visa_process.group_service_request_payroll_manager').users
                for user in payroll_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on  Payroll Approval',
                        note='A Payroll has been sent for approval requires your action.'
                        )
        return result
    def action_reviewed_by_hr_manager(self):
        result=super(ClientPayslipApproval, self).action_reviewed_by_hr_manager()
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
                hr_manager_users = self.env.ref('visa_process.group_service_request_hr_employee').users
                for user in hr_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on  Payslip Approval',
                        note='A Payslip has been verified by PM and reviewd requires your action.'
                        )
                
        
        return result
    def action_submit_to_payroll_employee(self):
        result=super(ClientPayslipApproval, self).action_submit_to_payroll_employee()
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
                payroll_employee_users = self.env.ref('visa_process.group_service_request_payroll_employee').users
                for user in payroll_employee_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Verified Payroll Approval',
                        note='A Payroll has been verified by PM requires your action.'
                        )
        
        return result
    
    def action_reviewed_by_payroll_employee(self):
        result=super(ClientPayslipApproval, self).action_reviewed_by_payroll_employee()
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

class ClientPayslipRefuseWizard(models.TransientModel):
    _inherit = 'client.payslip.refuse.wizard'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
    
    def refuse_payslip(self):
        result=super(ClientPayslipRefuseWizard, self).refuse_payslip()
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
                payroll_manager_users = self.env.ref('visa_process.group_service_request_payroll_employee').users
                for user in payroll_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Verified Payslip Approval',
                        note='A Payslip has been verified by PM requires your action.'
                        )
        
        return result
            




