from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrEmployeeChangeRequestRejectWizard(models.TransientModel):
    _name = 'hr.employee.change.request.reject.wizard'
    _description = 'Reject Employee Change Request Wizard'

    reject_reason = fields.Text(string='Reason for Rejection')

    def action_confirm_reject(self):
        self.ensure_one()
        context = self.env.context
        active_ids = context.get('active_ids', [])
        active_model = context.get('active_model') 

        if not active_ids or not active_model:
            return {'type': 'ir.actions.act_window_close'}

        if active_model == 'hr.employee.change.request':
            records = self.env['hr.employee.change.request'].browse(active_ids)
            for rec in records:
                if rec.state != 'pending':
                    raise UserError(_('Only pending employee change requests can be rejected.'))
                rec.write({
                    'state': 'rejected',
                    'reject_reason': self.reject_reason,
                    'approved_by': self.env.user.id,
                    'approval_date': fields.Datetime.now(),
                })
                rec.activity_update_for_employee()
                rec._notify_employee_status_update()

        elif active_model == 'hr.business.trip':
            records = self.env['hr.business.trip'].browse(active_ids)
            for rec in records:
                if rec.state in ('draft', 'approve_businees_trip', 'refuse'):
                    raise UserError(_("Business trip requests in state 'Draft', 'Done', or 'Refused' cannot be rejected."))
                rec.write({
                    'state': 'refuse',  
                    'reject_reason': self.reject_reason,
                })
                rec.message_post(body=_("Business trip request has been **Rejected**.<br/>Reason: %s") % self.reject_reason)
        elif active_model == 'hr.eos.request':
            records = self.env['hr.eos.request'].browse(active_ids)
            for rec in records:
                if rec.state in ('draft', 'refuse'):
                    raise UserError(_("End of Service requests in state 'Draft', 'Done', or 'Refused' cannot be rejected."))
                rec.write({
                    'state': 'refuse',  
                    'reject_reason': self.reject_reason,
                })
                rec.message_post(body=_("End of Service request has been **Rejected**.<br/>Reason: %s") % self.reject_reason)
        elif active_model == 'hr.end.of.contract':
            records = self.env['hr.end.of.contract'].browse(active_ids)
            for rec in records:
                if rec.state in ('draft', 'refuse'):
                    raise UserError(_("End of contract requests in state 'Draft', 'Done', or 'Refused' cannot be rejected."))
                rec.write({
                    'state': 'refuse',  
                    'reject_reason': self.reject_reason,
                })
                rec.message_post(body=_("End of contract request has been **Rejected**.<br/>Reason: %s") % self.reject_reason)
        elif active_model == 'hr.annual.request':
            records = self.env['hr.annual.request'].browse(active_ids)
            for rec in records:
                if rec.state in ('draft', 'refuse'):
                    raise UserError(_("annual requests in state 'Draft', 'Done', or 'Refused' cannot be rejected."))
                rec.write({
                    'state': 'refuse',  
                    'reject_reason': self.reject_reason,
                })
                rec.message_post(body=_("Air Ticket request has been **Rejected**.<br/>Reason: %s") % self.reject_reason)

           
        return {'type': 'ir.actions.act_window_close'}