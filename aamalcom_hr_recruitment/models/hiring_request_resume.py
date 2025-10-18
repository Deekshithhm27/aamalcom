from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HiringRequestResume(models.Model):
    _name = 'recruitment.hiring.request.resume'
    _description = 'Resume Uploaded for Hiring Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Candidate Name', required=True)
    attachment = fields.Binary(string='Resume File', required=True)
    filename = fields.Char(string='Filename')
    state = fields.Selection([
        ('new', 'New'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected')
    ], string='Status', default='new', tracking=True,store=True)
    hiring_request_id = fields.Many2one('recruitment.hiring.request', string='Hiring Request', required=True, ondelete='cascade')
    uploaded_by = fields.Many2one('res.users', string='Uploaded By', readonly=True, default=lambda self: self.env.uid)
    upload_date = fields.Datetime(string='Upload Date', readonly=True, default=fields.Datetime.now)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    application_ref = fields.Many2one('hr.applicant',string="Application Ref")

    def action_shortlist(self):
        for rec in self:
            rec.state = 'shortlisted'
            rec.message_post(body=_("Resume shortlisted"))

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body=_("Resume rejected"))