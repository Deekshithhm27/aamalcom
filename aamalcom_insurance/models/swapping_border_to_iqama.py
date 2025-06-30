# File: aamalcom_insurance/models/medical_insurance_deletion.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SwappingBorderToIqama(models.Model):
    _name = 'swapping.border.to.iqama'
    _description = 'Swapping Border to Iqama'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        group_pm = self.env.ref('visa_process.group_service_request_manager')
        if group_pm:
            res['project_manager_id'] = self.env.user.partner_id.id
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
            res['project_manager_id'] = self.env.user.partner_id.company_spoc_id.id
        return res

    name = fields.Char(string='Request Reference', copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,domain="[('client_parent_id','=',client_parent_id)]")
    service_enquiry_id = fields.Many2one('service.enquiry', string='Service Enquiry')
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('review_to_be_done', 'Review to be Done'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    swapping_type = fields.Selection([('employee','Employee'),('dependents','Employee Dependents')],string="Swapping Type",default="employee")

    digital_iqama_copy = fields.Binary(string="Digital Iqama Copy")
    cchi_confirmation_document = fields.Binary(string="CCHI Confirmation Document")

    residance_doc = fields.Binary(string="Residance Doc")
    muqeem_print_doc = fields.Binary(string="Muqeem Print Doc")

    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('swapping.border.to.iqama')
        res = super(SwappingBorderToIqama,self).create(vals)
        return res

    @api.onchange('swapping_type','employee_id')
    def _onchange_deletion_type(self):
        if self.swapping_type == 'employee':
            return {'domain': {'service_enquiry_id': [('service_request', '=', 'hr_card'),('employee_id','=',self.employee_id.id)]}}

    @api.onchange('service_enquiry_id')
    def update_document(self):
        for line in self:
            if line.service_enquiry_id.service_request == 'hr_card':
                line.residance_doc = line.service_enquiry_id.residance_doc
                line.muqeem_print_doc = line.service_enquiry_id.muqeem_print_doc

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def action_submit(self):
        for line in self:
            line.state = 'submitted'

    def action_submit_to_review(self):
        for line in self:
            if not self.cchi_confirmation_document:
                raise UserError('Upload CCHI Confirmation Document.')
            line.state = 'review_to_be_done'


    def action_done(self):
        for line in self:
            line.state = 'done'