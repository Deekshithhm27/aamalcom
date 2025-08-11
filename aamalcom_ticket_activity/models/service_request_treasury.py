from odoo import models, fields

class ServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    def _schedule_ticket_treasury_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit(self):
        result = super(ServiceRequestTreasury, self).action_submit()
        # Automatically approve the activity
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_id.action_feedback(feedback='Approved')
        # Delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_ids.unlink()
        # Schedule a new activity for the responsible users
        fm_users = self.env.ref('visa_process.group_service_request_finance_manager').users
        for user in fm_users:
            self._schedule_ticket_treasury_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Take action (Upload confirmation document) for the submission made by the Treasury Department.'
            )
        return result

    def action_upload_confirmation(self):
        result = super(ServiceRequestTreasury, self).action_upload_confirmation()
        for line in self:
            # Automatically approve and unlink existing activities
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            # Define variables once to use in the entire if/elif block
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            govt_users = self.env.ref('visa_process.group_service_request_employee').users
            first_govt_employee_id = line.service_request_id.first_govt_employee_id.user_id.id

            
            if line.service_request_id.service_request == 'transfer_req':
                for user in govt_users:
                    line.service_request_id._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Payment confirmation) on this ticket.'
                    )
            elif line.service_request_id.service_request == 'prof_change_qiwa':
                for user in govt_users:
                    line.service_request_id._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Upload documents) on this ticket.'
                    )
            elif line.service_request_id.service_request == 'hr_card':
                line.service_request_id._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            elif line.service_request_id.service_request in ['iqama_renewal', 'prof_change_qiwa']:
                line.service_request_id._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Second govt employee need to be assigned) on this ticket.'
                )
            elif line.service_request_id.service_request == 'medical_blood_test':
                line.service_request_id._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (First govt employee need to be assigned) on this ticket.'
                )
            elif line.service_request_id.service_request == 'ajeer_permit':
                line.service_request_id._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            # You had repeated code blocks for visa_cancellation, dependents_ere, and salary_advance
            # The logic to approve and unlink activities is already at the beginning of the method.
            # I've removed the redundant code.
            
            # This is the catch-all `elif` for any other service requests
            elif line.service_request_id.service_request not in [
                'transfer_req', 'hr_card', 'iqama_renewal', 'prof_change_qiwa', 
                'medical_blood_test', 'ajeer_permit', 'visa_cancellation', 
                'dependents_ere', 'salary_advance'
            ]:
                line.service_request_id._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (First govt employee need to be assigned) on this ticket.'
                )
        return result