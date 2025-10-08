from odoo import models, fields, api, _

class HrServiceRequestTreasury(models.Model):
    _inherit = 'hr.service.request.treasury'

    def _schedule_ticket_treasury_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=False,
            summary=summary,
            note=note,
            user_id=user_id
        )
    
    def action_update_treasury(self):
        result = super(HrServiceRequestTreasury, self).action_update_treasury()
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
            if self.service_request_ref and self.service_request_ref._name == 'hr.medical.blood.test':
                operations_manager_group = self.env.ref(
                    'visa_process.group_service_request_operations_manager',
                    raise_if_not_found=False
                )

                if operations_manager_group:
                    for user in operations_manager_group.users:
                        self._schedule_ticket_treasury_activity(
                            user_id=user.id,
                            summary='Action Required - Treasury Updated',
                            note='Treasury has submitted the Medical Blood Test request for your approval.'
                        )
        return result
    
    def action_upload_confirmation(self):
        result = super(HrServiceRequestTreasury, self).action_upload_confirmation()
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
            payroll_manager_group = self.env.ref('visa_process.group_service_request_payroll_manager')
            hr_employee_group = self.env.ref('visa_process.group_service_request_hr_employee')
            target_users = self.env['res.users']
            if self.service_request_ref:
                model_name = self.service_request_ref._name
                if model_name == 'loan.request' and payroll_manager_group:
                    target_users = payroll_manager_group.users
                elif model_name in ['hr.medical.blood.test', 'hr.exit.reentry'] and hr_employee_group:
                    target_users = hr_employee_group.users
            for user in target_users:
                self._schedule_ticket_treasury_activity(
                    user_id=user.id,
                    summary='Action Required on Treasury Request',
                    note=f'Payment Confirmation Uploaded. Please review and take further action.'
                )

        return result
