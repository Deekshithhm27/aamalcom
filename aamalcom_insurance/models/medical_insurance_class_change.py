from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MedicalInsuranceClassChange(models.Model):
    _name = 'medical.insurance.class.change'
    _description = 'Medical Insurance Upgrade/Downgrade'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
            res['project_manager_id'] = self.env.user.partner_id.company_spoc_id.id
        return res

    name = fields.Char(string="Reference",copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('submitted_to_service_provider', 'Submitted to Service Provider'),
        ('submitted_to_pm','Submitted to PM'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")
    employee_id = fields.Many2one('hr.employee',string="Employee",required=True,domain="[('client_parent_id','=',client_parent_id)]")
    change_type = fields.Selection([
        ('upgrade', 'Upgrade'),
        ('downgrade', 'Downgrade')
    ], string='Change Type', required=True)
    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_silver+','SILVER+'),('class_silver','SILVER'),('class_a+','A+'),('class_a','A'),('class_b+','B+'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",required=True,tracking=True)

    muqeem_iqama_document = fields.Binary(string="Muqeem/Iqama Document")
    cchi_confirmation_document = fields.Binary(string="CCHI Confirmation Document")
    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.insurance.class.change')
        res = super(MedicalInsuranceClassChange,self).create(vals)
        return res
    

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def action_submit(self):
        for line in self:
            line.state = 'submitted'

    def action_submit_to_provider(self):
        for line in self:
            if not self.muqeem_iqama_document:
                raise UserError('Upload Muqeem/Iqama Document before submitting to Service Provider.')
            line.state = 'submitted_to_service_provider'

    def action_submit_to_pm(self):
        for line in self:
            if not self.cchi_confirmation_document:
                raise UserError('Upload CCHI Confirmation Document before submitting to PM.')
            line.state = 'submitted_to_pm'

    def action_done(self):
        for line in self:
            line.state = 'done'

