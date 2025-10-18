from odoo import api, fields, models, _

class HrOnboardingChecklist(models.Model):
    _name = 'hr.onboarding.checklist'
    _description = 'Onboarding Checklist'
    _order = 'sequence,id'  # This is crucial!

    ref_id = fields.Char(string='Request ID', readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.onboarding.checklist'))

    name = fields.Char(string="Name", store=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10) # Set a default value to avoid issues
    is_done = fields.Boolean(string='Completed')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
