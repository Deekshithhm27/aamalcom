from odoo import models, fields

class LifeInsuranceDeletion(models.Model):
    _inherit = 'life.insurance.deletion'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
        

    def action_submit(self):
        result = super(LifeInsuranceDeletion, self).action_submit()
        insurance_users = self.env.ref('visa_process.group_service_request_insurance_employee').users
        for user in insurance_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action  on this ticket.'
                )
        return result

    def action_get_confirmation(self):               
        result = super(LifeInsuranceDeletion, self).action_get_confirmation()
        for line in self:
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id

            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            group = self.env.ref('visa_process.group_service_request_employee')
            users = group.users
            for line in users:
                self._schedule_ticket_activity(
                    user_id=line.id,
                    summary='Ticket Ready for GE Review',
                    note='Please review the approved request and proceed.'
                )
        return result

    def action_govt_confirm(self):
        result = super(LifeInsuranceDeletion, self).action_govt_confirm()

        for line in self:
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id

            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')
            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            if client_manager_user_id:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                )
            
        return result

    def action_docs_uploaded(self):
        result = super(LifeInsuranceDeletion, self).action_docs_uploaded()
        for line in self:
            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')
            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            insurance_users = self.env.ref('visa_process.group_service_request_insurance_employee').users
            for user in insurance_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                    )
        return result


    def action_pm_confirm_exit(self):
        result = super(LifeInsuranceDeletion, self).action_pm_confirm_exit()
        for line in self:
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id

            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()

            if client_manager_user_id:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action  on this ticket.'
                )
        return result

    def action_insurance_confirm(self):
        result = super(LifeInsuranceDeletion, self).action_insurance_confirm()
        for line in self:
            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            insurance_users = self.env.ref('visa_process.group_service_request_insurance_employee').users
            for user in insurance_users:
                self._schedule_ticket_activity(
                    user_id=user.id,
                    summary='Action Required on Ticket',
                    note='Govt Team Confirmation Recieved.'
                    )
        return result

    def action_insurance_confirm(self):
        result = super(LifeInsuranceDeletion, self).action_insurance_confirm()
        for line in self:
            # Approve current user's activity
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')

            # Remove other users' activities
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', line.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
