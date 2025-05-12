from odoo import models, fields, api

class RefuseReasonWizard(models.TransientModel):
    _name = 'refuse.reason.wizard'
    _description = 'Refuse Reason Wizard'

    reason = fields.Text(string='Reason', required=True)

    def action_submit_refusal(self):
        active_id = self.env.context.get('active_id')
        record = self.env['service.enquiry'].browse(active_id)
        record.write({
            'state': 'refuse',
            'refuse_reason': self.reason,
            'assign_govt_emp_one': True,
            'assigned_govt_emp_one': False,
        })
        return {'type': 'ir.actions.act_window_close'}
