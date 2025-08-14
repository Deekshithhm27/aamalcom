from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MedicalInsuranceDeletion(models.Model):
    _inherit = 'medical.insurance.deletion'

    def _schedule_ticket_activity_mid(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_mid_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )

    def action_submit(self):
        result = super().action_submit()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        for user in users:
            self._schedule_ticket_activity_mid(
                user_id=user.id,
                summary='Action Required on Ticket',
                note='Do review and give confirmation for this ticket.'
            )
        return result

    def action_get_confirmation(self):
        result = super().action_get_confirmation()
        group = self.env.ref('visa_process.group_service_request_employee')
        users = group.users
        for user in users:
            self._schedule_ticket_activity_mid(
                user_id=user.id,
                summary='Ticket Ready for GE Review',
                note='Please review the approved request and proceed.'
            )
        return result

    def action_govt_confirm(self):
        self.ensure_one()

        if not self.is_inside_ksa and not self.is_outside_ksa:
            raise UserError("Choose whether Employee is Inside or Outside KSA before confirming.")

        # Call parent method
        super(MedicalInsuranceDeletion, self).action_govt_confirm()

        # Notify GE users
        group = self.env.ref('visa_process.group_service_request_employee')
        users = group.users
        for user in users:
            self._schedule_ticket_activity_mid(
                user_id=user.id,
                summary='Ticket Ready for GE Review',
                note='Please review the approved request and proceed.'
            )

        # Notify Project Manager only here
        if self.project_manager_id and self.project_manager_id.user_id:
            self._schedule_ticket_activity_mid(
                user_id=self.project_manager_id.user_id.id,
                summary='Ticket Ready for PM Review',
                note='Please review the approved request and proceed.'
            )

        return True

    def action_pm_confirm_exit(self):
        # Avoid any PM notification here
        self.ensure_one()
        self.confirmed_by_pm = self.env.user.id
        self.is_outside_ksa = True
        self.is_inside_ksa = False
        self.state = 'exit_confirmed'
        return True

    def action_insurance_confirm(self):
        result = super().action_insurance_confirm()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        for user in users:
            self._schedule_ticket_activity_mid(
                user_id=user.id,
                summary='Ticket Reviewed by GE',
                note='Govt team confirmation received.'
            )
        return result





        
    