from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class TerminationService(models.Model):
    _name = "termination.request"
    _description = "Termination Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('reject', 'Rejected'),
            ('submitted_to_hr', 'Submitted to HR'),
            ('approved_by_hr', 'Reviewed By HR'),
            ('submitted_to_pm', 'Submitted to PM'),
            ('approved', 'Approved'),
            ('done', 'Done'),
        ], string="Status", default="draft", tracking=True)

    termination_type = fields.Selection([
        ('termination_request', 'Termination'),
    ], string='Service Request', required=True)

    # New default_get method to pre-fill client fields for specific user groups
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
        return res

    client_id = fields.Many2one('res.partner', string="Client Spoc")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    client_parent_id = fields.Many2one(
        'res.partner',
        string="Client",
        domain="[('is_company','=',True),('parent_id','=',False)]",
        store=True
    )
    name = fields.Char(string="Reference", copy=False,default=lambda self: self.env['ir.sequence'].next_by_code('termination.request'))
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

    iqama_no = fields.Char(string="Iqama No")
    identification_id = fields.Char(string='Border No.')
    passport_no = fields.Char(string='Passport No')
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    upload_proof_of_request_doc=fields.Binary(string="Proof of Request Document")
    reason_of_termination=fields.Char(string="Reason of Termination")
    upload_termination_doc = fields.Binary(string="Termination Document")
    def action_submitted(self):
        for record in self:
            record.state = 'submit'

    

    def action_process_done(self):
        for record in self:
            record.state = 'done'



