from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class HiringRequestRejectWizard(models.TransientModel):
    _name = 'hiring.request.reject.wizard'
    _description = 'Reject Hiring Request Wizard'

    request_ids = fields.Many2many('recruitment.hiring.request', string='Requests')
    reject_reason = fields.Text(string='Reject Reason', required=True)
    reject_state = fields.Selection([
        ('reject', 'Recruitment Officer Rejected'),
        ('admin_rejected', 'Recruitment Administrator Rejected'),
        ('gm_rejected', 'General Manager Rejected'),
    ], string='Rejection State', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        ctx = self.env.context
        requests = ctx.get('default_request_ids') or ctx.get('active_ids')
        if requests:
            res['request_ids'] = [(6, 0, requests)]
        if ctx.get('reject_state'):
            res['reject_state'] = ctx['reject_state']
        return res

    def action_confirm_reject(self):
        for rec in self.request_ids:
            rec.set_reject_reason(self.reject_reason, self.reject_state)
        return {'type': 'ir.actions.act_window_close'}