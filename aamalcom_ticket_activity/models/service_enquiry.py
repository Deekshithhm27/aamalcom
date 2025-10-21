from odoo import models, fields

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    def _schedule_ticket_activity(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit(self):
        result = super(ServiceEnquiry, self).action_submit()
        client_manager_user_id = self.env.user.company_spoc_id.user_id.id
        for line in self:
            if line.service_request in ['new_ev'] and line.aamalcom_pay:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Approval) on this ticket.'
                )
            elif line.service_request == 'iqama_card_req':
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (confirmation on payment) on this ticket.'
                )
            elif line.service_request in ['exit_reentry_issuance_ext','exit_reentry_issuance'] and line.aamalcom_pay:
                operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )
            else:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Employee needs to be assigned) on this ticket.'
                )
        return result
    def open_assign_employee_wizard(self):
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for line in self:
            if line.service_request in ['muqeem_dropout']:
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
            
        return result


    def action_require_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_require_payment_confirmation()
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
            # client spoc user id
            partner_id = line.client_id.id
            # Search for the user whose partner_id matches this partner
            user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
            if user:
                user_id = user.id
                self._schedule_ticket_activity(
                    user_id=user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Payment confirmation Document) on this ticket.'
                )
        return result

    def action_new_ev_require_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_new_ev_require_payment_confirmation()
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
            # client spoc user id
            partner_id = line.client_id.id
            # Search for the user whose partner_id matches this partner
            user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
            if user:
                user_id = user.id
                self._schedule_ticket_activity(
                    user_id=user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Payment confirmation Document) on this ticket.'
                )
        return result

    def action_new_ev_submit_for_approval(self):
        result = super(ServiceEnquiry, self).action_new_ev_submit_for_approval()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_submit_for_approval(self):
        result = super(ServiceEnquiry, self).action_submit_for_approval()
        for line in self:
            if line.service_request == 'transfer_req':
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
                # client spoc user id
                partner_id = line.client_id.id
                # Search for the user whose partner_id matches this partner
                user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
                if user:
                    user_id = user.id
                    self._schedule_ticket_activity(
                        user_id=user_id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )
            else:
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
                operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
                for user in operations_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Approval) on this ticket.'
                    )
        return result

    def action_client_spoc_approve(self):
        result = super(ServiceEnquiry, self).action_client_spoc_approve()
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
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            self._schedule_ticket_activity(
                user_id=client_manager_user_id,
                summary='Action Required on Ticket',
                note='Do review and take action (Require confirmation on payment) on this ticket.'
            )
        return result

    def action_op_approved(self):
        result = super(ServiceEnquiry, self).action_op_approved()
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
        gm_users = self.env.ref('visa_process.group_service_request_general_manager').users
        for user in gm_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action(Approval) on this ticket.'
            )
        return result

    def action_gm_approved(self):
        result = super(ServiceEnquiry, self).action_gm_approved()
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

    def action_request_fin_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_request_fin_payment_confirmation()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_finance_approved(self):
        result = super(ServiceEnquiry, self).action_finance_approved()
        for line in self:
            treasury_id = self.env['service.request.treasury'].search([('service_request_id', '=', line.id)])
            if treasury_id:
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
                    treasury_id._schedule_ticket_treasury_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Do review and take action (Submission pending for the treasury department).'
                    )
        return result

    def action_new_ev_docs_uploaded(self):
        result = super(ServiceEnquiry, self).action_new_ev_docs_uploaded()
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
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            self._schedule_ticket_activity(
                user_id=client_manager_user_id,
                summary='Action Required on Ticket',
                note='Do review and take action (Employee needs to be assigned) on this ticket.'
            )
        return result

    def action_submit_payment_confirmation(self):
        result = super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for line in self:
            if line.service_request in ['exit_reentry_issuance_ext']:
                # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            elif line.service_request in ['ajeer_permit']:
                # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            elif line.service_request in ['hr_card']:
                # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Payment Confirmation')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                second_govt_employee_id = line.second_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=second_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            elif line.service_request in ['bank_loan', 'vehicle_lease', 'apartment_lease', 'bank_letter', 'car_loan', 
                                       'rental_agreement', 'exception_letter', 'attestation_waiver_letter', 
                                       'embassy_letter', 'istiqdam_letter', 'sce_letter', 'bilingual_salary_certificate', 
                                       'contract_letter', 'bank_account_opening_letter', 'bank_limit_upgrading_letter',
                                       'cultural_letter', 'emp_secondment_or_cub_contra_ltr','employment_contract','salary_certificate','istiqdam_form','family_visa_letter','family_resident']:
                # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Payment Confirmation')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            
            else:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Employee needs to be assigned) on this ticket.'
                )
        return result

    # function-government employee submits the iqama print documents to the PM
    def action_iqama_uploaded(self):
        result = super(ServiceEnquiry, self).action_iqama_uploaded()
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
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            self._schedule_ticket_activity(
                user_id=client_manager_user_id,
                summary='Action Required on Ticket',
                note='Do review and take action (send confirmation to the client and close) on this ticket.'
            )
        return result

    def action_doc_uplaod_submit(self):
        result = super(ServiceEnquiry, self).action_doc_uplaod_submit()

        for line in self:
            if line.service_request in ['hr_card']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                line._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Second govt employee need to be assigned) on this ticket.'
                )
    def action_doc_uplaod_submit_self_pay(self):
        result = super(ServiceEnquiry, self).action_doc_uplaod_submit_self_pay()
        for line in self:
            if line.service_request in ['hr_card']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                line._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Second govt employee need to be assigned) on this ticket.'
                )

    def action_valid_ere(self):
        result = super(ServiceEnquiry, self).action_valid_ere()
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
            partner_id = line.client_id.id
            client_spoc_user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
            if client_spoc_user:
                self._schedule_ticket_activity(
                    user_id=client_spoc_user.id,
                    summary='ERE Still Valid - Action Required',
                    note='The ERE is still valid. The request can be re initiated after expiry on.'
                )
        return result

    def action_submit_initiate(self):
        result = super(ServiceEnquiry, self).action_submit_initiate()
        client_manager_user_id = self.env.user.company_spoc_id.user_id.id
        for line in self:
            #muqeem dropout
            # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', self.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=',
                 self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            if activity_id:
                activity_id.action_feedback(feedback='Done')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Ticket Resubmitted, Employee needs to be assigned) on this ticket.'
                )
            else:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Employee needs to be assigned) on this ticket.'
                )
        return result

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for line in self:
            if line.service_request == 'prof_change_qiwa':
                treasury_id = self.env['service.request.treasury'].search([('service_request_id', '=', line.id)])
                if treasury_id:
                    for srt in treasury_id:
                        if srt.state == 'done':
                            # Automatically approve the activity if the user forgot to mark it as done
                            activity_id = self.env['mail.activity'].search([
                                ('res_id', '=', self.id),
                                ('user_id', '=', self.env.user.id),
                                ('activity_type_id', '=',
                                 self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                            ])
                            activity_id.action_feedback(feedback='Approved')
                            # If one user completes the activity or action on the record, delete activities for other users
                            activity_ids = self.env['mail.activity'].search([
                                ('res_id', '=', self.id),
                                ('activity_type_id', '=',
                                 self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                            ])
                            activity_ids.unlink()
                else:
                    # Automatically approve the activity if the user forgot to mark it as done
                    activity_id = self.env['mail.activity'].search([
                        ('res_id', '=', self.id),
                        ('user_id', '=', self.env.user.id),
                        ('activity_type_id', '=',
                         self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_id.action_feedback(feedback='Approved')
                    # If one user completes the activity or action on the record, delete activities for other users
                    activity_ids = self.env['mail.activity'].search([
                        ('res_id', '=', self.id),
                        ('activity_type_id', '=',
                         self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                    ])
                    activity_ids.unlink()


            else:
                # Automatically approve the activity if the user forgot to mark it as done
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
            return result

    def action_iqama_payment_received_confirmation(self):
        result = super(ServiceEnquiry, self).action_iqama_payment_received_confirmation()
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
            client_manager_user_id = line.client_id.company_spoc_id.user_id.id
            self._schedule_ticket_activity(
                user_id=client_manager_user_id,
                summary='Action Required on Ticket',
                note='Do review and take action (Employee needs to be assigned) on this ticket.'
            )
        return result

    def action_iqama_process_complete(self):
        result = super(ServiceEnquiry, self).action_iqama_process_complete()
        # Automatically approve the activity if the user forgot to mark it as done
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_id.action_feedback(feedback='Approved')
        # If one user completes the activity or action on the record, delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_ids.unlink()
        return result

    def action_submit_doc_uploaded_final_exit(self):
        result=super(ServiceEnquiry,self).action_submit_doc_uploaded_final_exit()
        # Automatically approve the activity if the user forgot to mark it as done
        for line in self:
            if line.service_request in ['final_exit_issuance']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Confirm Inside/Outside KSA) on this ticket.'
                ) 
                
                
        return result

   

    def action_submit_for_review_final_exit(self):
        result=super(ServiceEnquiry, self).action_submit_for_review_final_exit()
        for line in self:
            if line.service_request in ['final_exit_issuance']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                            user_id=first_govt_employee_id,
                            summary='Action Required on Ticket',
                            note='Do review and take action on (Approval of Last Working Date)  this ticket.'
                        )  
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])      
                
        return result

    def final_exit_submit_inside(self):
        result=super(ServiceEnquiry, self).final_exit_submit_inside()
        for line in self:
            if line.service_request in ['final_exit_issuance']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Assign Employee ) on this ticket.'
                )
        return result

    def final_exit_submit(self):
        result=super(ServiceEnquiry, self).final_exit_submit()
        for line in self:
            if line.service_request in ['final_exit_issuance']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
        return result

    def action_submit_to_ministry(self):
        result=super(ServiceEnquiry, self).action_submit_to_ministry()
        for line in self:
            if line.service_request in ['visa_cancellation']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
        return result

    def action_approved_by_ministry(self):
        result=super(ServiceEnquiry, self).action_approved_by_ministry()
        for line in self:
            if line.service_request in ['visa_cancellation']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
        return result

    def action_submit_to_treasury_visa_cancellation(self):
        result=super(ServiceEnquiry, self).action_submit_to_treasury_visa_cancellation()
        for line in self:
            if line.service_request in ['visa_cancellation']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                fm_users = self.env.ref('visa_process.group_service_request_finance_manager').users
                for user in fm_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Ticket',
                        note='Take action  for this request.'
                    )
                
        return result

    def action_salary_increase_submit_for_approval(self):
        result=super(ServiceEnquiry, self).action_salary_increase_submit_for_approval()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_first_govt_emp_submit_salary(self):
        result=super(ServiceEnquiry, self).action_first_govt_emp_submit_salary()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['salary_increase_process']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Assign Employee) on this ticket.'
                )
        
        return result

    def action_second_govt_emp_submit_salary(self):
        result=super(ServiceEnquiry, self).action_second_govt_emp_submit_salary()
        for line in self:
            if line.service_request in ['salary_increase_process']:
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
                        summary='Action Required on Salary Increase Process',
                        note='A Salary Increase Process ticket requires your action. Please review and take action.'
                        )
    
        return result

    def action_process_complete_salary_increase(self):
        result=super(ServiceEnquiry, self).action_process_complete_salary_increase()
        for line in self:
            if line.service_request in ['salary_increase_process']:
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_id.action_feedback(feedback='Approved')
                # If one user completes the activity or action on the record, delete activities for other users
                activity_ids = self.env['mail.activity'].search([
                    ('res_id', '=', self.id),
                    ('activity_type_id', '=',
                     self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
                ])
                activity_ids.unlink()
                
        return result

    def action_salary_advance_submit_for_approval(self):
        result=super(ServiceEnquiry, self).action_salary_advance_submit_for_approval()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_doc_uploaded_probation(self):
        result=super(ServiceEnquiry, self).action_doc_uploaded_probation()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['probation_request']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Upload Documents) on this ticket.'
                )
        
        return result
    def action_process_complete_probation(self):
        result=super(ServiceEnquiry, self).action_process_complete_probation()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['probation_request']:
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

    def action_submit_to_treasury(self):
        result = super(ServiceEnquiry, self).action_submit_to_treasury()
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
                note='Do review and take action(Approval by treasury) on this ticket.'
            )
        return result

    def action_finance_submit_to_treasury(self):
        result = super(ServiceEnquiry, self).action_finance_submit_to_treasury()
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

    def action_first_govt_emp_submit(self):
        result=super(ServiceEnquiry, self).action_first_govt_emp_submit()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['final_clearance']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Assign Employee) on this ticket.'
                )
        
        return result

    def action_submit_to_hr(self):
        result=super(ServiceEnquiry, self).action_submit_to_hr()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['final_clearance']:
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
                payroll_manager_users = self.env.ref('visa_process.group_service_request_hr_manager').users
                for user in payroll_manager_users:
                    self._schedule_ticket_activity(
                        user_id=user.id,
                        summary='Action Required on Salary Increase Process',
                        note='A Salary Increase Process ticket requires your action. Please review and take action.'
                        )
    
        return result

    def action_approve_by_hr(self):
        result=super(ServiceEnquiry, self).action_approve_by_hr()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['final_clearance']:
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
                second_govt_employee_id = line.second_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=second_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
        return result

    def action_process_complete_final_clearance(self):
        result=super(ServiceEnquiry, self).action_process_complete_final_clearance()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['final_clearance']:
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

    def action_ajeer_permit_submit_for_approval(self):
        result=super(ServiceEnquiry, self).action_ajeer_permit_submit_for_approval()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_submit_for_review_courier(self):
        result=super(ServiceEnquiry, self).action_submit_for_review_courier()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['courier_charges']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action on this ticket.'
                )
        
        return result
    def action_approve(self):
        result=super(ServiceEnquiry, self).action_approve()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['courier_charges']:
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
                first_govt_employee_id = line.first_govt_employee_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=first_govt_employee_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
        return result

    def action_dependents_ere_submit_for_approval(self):
        result=super(ServiceEnquiry, self).action_dependents_ere_submit_for_approval()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def update_hr_card_amount(self):
        result=super(ServiceEnquiry, self).update_hr_card_amount()
        # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
        for line in self:
            if line.service_request in ['hr_card']:
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
                client_manager_user_id = line.client_id.company_spoc_id.user_id.id
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action(Assign Employee) on this ticket.'
                )
        
        return result

    def update_jawazat_amount(self):
        result=super(ServiceEnquiry, self).update_jawazat_amount()
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
        operations_manager_users = self.env.ref('visa_process.group_service_request_operations_manager').users
        for user in operations_manager_users:
            self._schedule_ticket_activity(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and take action (Approval) on this ticket.'
            )
        return result

    def action_process_complete_without_mofa(self):
        result=super(ServiceEnquiry, self).action_process_complete_without_mofa()
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



    def action_process_complete_letter_head(self):
        result=super(ServiceEnquiry, self).action_process_complete_letter_head()
        # Automatically approve the activity if the user forgot to mark it as done
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_id.action_feedback(feedback='Approved')
        # If one user completes the activity or action on the record, delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_ids.unlink()

    def action_process_complete_letter_head(self):
        result=super(ServiceEnquiry, self).action_process_complete_letter_head()
        # Automatically approve the activity if the user forgot to mark it as done
        activity_id = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('user_id', '=', self.env.user.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_id.action_feedback(feedback='Approved')
        # If one user completes the activity or action on the record, delete activities for other users
        activity_ids = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('activity_type_id', '=',
             self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
        ])
        activity_ids.unlink()


























