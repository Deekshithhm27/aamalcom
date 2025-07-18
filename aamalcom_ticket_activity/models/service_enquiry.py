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
            if line.service_request in ['new_ev', 'exit_reentry_issuance_ext'] and line.aamalcom_pay:
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
            else:
                self._schedule_ticket_activity(
                    user_id=client_manager_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Employee needs to be assigned) on this ticket.'
                )
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





















