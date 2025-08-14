from odoo import models, fields

class LifeInsuranceDeletion(models.Model):
    _inherit = 'life.insurance.deletion'

    def _schedule_ticket_activity_lid(self, user_id, summary, note):
        self.activity_schedule(
            act_type_xmlid='aamalcom_ticket_activity.mail_activity_type_ticket_lid_action',
            date_deadline=None,
            summary=summary,
            note=note,
            user_id=user_id
        )
        

    def action_submit(self):
        result = super(LifeInsuranceDeletion, self).action_submit()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        for line in users:
            self._schedule_ticket_activity_lid(
                user_id=line.id,
                summary='Action Required on Ticket',
                note='Do review and give confirmation for this ticket.'
            )
        return result

    def action_get_confirmation(self):               
        result = super(LifeInsuranceDeletion, self).action_get_confirmation()
        group = self.env.ref('visa_process.group_service_request_employee')
        users = group.users
        for line in users:
            self._schedule_ticket_activity_lid(
                user_id=line.id,
                summary='Ticket Ready for GE Review',
                note='Please review the approved request and proceed.'
            )
        return result

    def action_pm_confirm_exit(self):
        result = super(LifeInsuranceDeletion, self).action_pm_confirm_exit()
        if self.project_manager_id:
            self._schedule_ticket_activity_lid(
                user_id=self.project_manager_id.user_id.id,
                summary='Ticket Ready for PM Review',
                note='Please review the approved request and proceed.'
            )
        return result

    def action_insurance_confirm(self):
        result = super(LifeInsuranceDeletion, self).action_insurance_confirm()
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        users = group.users
        for line in users:
            self._schedule_ticket_activity_lid(
                user_id=line.id,
                summary='Ticket Reviewed by GE',
                note='Govt team confirmation received.'
            )
        return result
