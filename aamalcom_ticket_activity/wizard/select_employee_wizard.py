from odoo import models, fields

class AssignEmployeeWizard(models.TransientModel):
    _inherit = 'assign.employee.wizard'

    def apply_selected_employee(self):
        result = super(AssignEmployeeWizard, self).apply_selected_employee()
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        departments = self.department_ids.mapped('name')
        if departments:
            # Automatically approve the activity if the user forgot to mark it as done before moving to the next state
            activity_id = self.env['mail.activity'].search([
                ('res_id', '=', active_enquiry.id),
                ('user_id', '=', self.env.user.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_id.action_feedback(feedback='Approved')
            # If one user completes the activity or action on the record, delete activities for other users
            activity_ids = self.env['mail.activity'].search([
                ('res_id', '=', active_enquiry.id),
                ('activity_type_id', '=', self.env.ref('aamalcom_ticket_activity.mail_activity_type_ticket_action').id),
            ])
            activity_ids.unlink()
            assign_employee_user_id = self.employee_id.user_id.id
            active_enquiry._schedule_ticket_activity(
                    user_id=assign_employee_user_id,
                    summary='Action Required on Ticket',
                    note='Do review and take action (Documents upload) on this ticket.'
                )
            
                
        return result