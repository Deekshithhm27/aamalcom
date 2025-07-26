from odoo import models, fields, api
from odoo.exceptions import UserError

class HrEmployeeChangeRequestRejectWizard(models.TransientModel):
    _name = 'hr.employee.change.request.reject.wizard'
    _description = 'Reject Employee Change Request Wizard'

    reject_reason = fields.Text(string='Reason for Rejection', required=True)

    def action_confirm_reject(self):
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            return

        change_requests = self.env['hr.employee.change.request'].browse(active_ids)
        for rec in change_requests:
            if rec.state != 'pending':
                raise UserError('Only pending requests can be rejected.')
            rec.write({
                'state': 'rejected',
                'reject_reason': self.reject_reason,
                'approved_by': self.env.user.id,
                'approval_date': fields.Datetime.now(),
            })
            rec.activity_update_for_employee()
            rec._notify_employee_status_update()