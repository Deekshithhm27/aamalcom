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
            self._schedule_ticket_treasury_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Take action (Upload confirmation document) for the submission made by the Treasury Department.'
            )
        return result

    def action_upload_confirmation(self):
        result = super(ServiceRequestTreasury, self).action_upload_confirmation()
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
            if line.service_request_id.service_request == 'transfer_req':
                govt_users = self.env.ref('visa_process.group_service_request_employee').users
                for user in govt_users:
                    line.service_request_id._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Payment confirmation) on this ticket.'
                    )
            if line.service_request_id.service_request == 'prof_change_qiwa':
                govt_users = self.env.ref('visa_process.group_service_request_employee').users
                for user in govt_users:
                    line.service_request_id._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Upload documents) on this ticket.'
                    )
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            if line.service_request_id.service_request not in ['transfer_req', 'hr_card', 'iqama_renewal',
                                                               'prof_change_qiwa']:
                line.service_request_id._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (First govt employee need to be assigned) on this ticket.'
                )
            if line.service_request_id.service_request in ['hr_card', 'iqama_renewal','prof_change_qiwa']:
                line.service_request_id._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Second govt employee need to be assigned) on this ticket.'
                )
        return result



