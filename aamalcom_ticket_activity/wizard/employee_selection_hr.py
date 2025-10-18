# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class AssignEmployeeMedicalWizard(models.TransientModel):
    _inherit = 'assign.employee.medical.wizard'

    def action_apply(self):
        result = super(AssignEmployeeMedicalWizard, self).action_apply()

        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')

        if active_model and active_id:
            leave = self.env[active_model].browse(active_id)

            if leave:
                # 1. Auto-complete current user's pending activity
                activity_id = self.env['mail.activity'].search([
                    ('res_id', '=', leave.id),
                    ('user_id', '=', self.env.user.id),
                    ('activity_type_id', '=', self.env.ref(
                        'aamalcom_ticket_activity.mail_activity_type_ticket_action'
                    ).id),
                ], limit=1)
                if activity_id:
                    activity_id.action_feedback(feedback=_("Approved"))

                # 2. Remove other users' activities for this leave
                other_activities = self.env['mail.activity'].search([
                    ('res_id', '=', leave.id),
                    ('activity_type_id', '=', self.env.ref(
                        'aamalcom_ticket_activity.mail_activity_type_ticket_action'
                    ).id),
                ])
                other_activities.unlink()

                # 3. Assign new activity to the selected employee’s user only
                if self.employee_id.user_id:
                    leave.activity_schedule(
                        'aamalcom_ticket_activity.mail_activity_type_ticket_action',
                        user_id=self.employee_id.user_id.id,
                        summary=_("Action Required on Leave"),
                        note=_("Please review and upload required documents for this leave request."),
                    )

        return result
