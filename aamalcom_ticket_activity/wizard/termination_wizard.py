from odoo import models, fields, api, _

class TerminationEmployeeWizard(models.TransientModel):
    _inherit = 'termination.assign.employee.wizard'

    def action_apply(self):
        result = super(TerminationEmployeeWizard, self).action_apply()

        termination = self.env['termination.request'].browse(self._context.get('active_id'))
        if termination:
            Activity = self.env['mail.activity']
            activity_type = self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action')

            #Complete the current user's activity (if any)
            current_activity = Activity.search([
                ('res_id', '=', termination.id),
                ('res_model', '=', 'termination.request'),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', activity_type.id),
            ], limit=1)
            if current_activity:
                current_activity.action_feedback(feedback=_("Approved"))

            #Remove all other users' pending activities except the current user
            other_activities = Activity.search([
                ('res_id', '=', termination.id),
                ('res_model', '=', 'termination.request'),
                ('activity_type_id', '=', activity_type.id),
                ('user_id', '!=', self.env.user.id)
            ])
            if other_activities:
                other_activities.unlink()

            #Create a new activity only for the selected employee’s user
            if self.employee_id.user_id:
                termination.activity_schedule(
                    activity_type_id=activity_type.id,
                    user_id=self.employee_id.user_id.id,
                    summary=_("Action Required on Termination"),
                    note=_("Please review and take required action."),
                )

        return result
