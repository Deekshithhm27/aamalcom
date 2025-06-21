from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LifeInsuranceEnrollment(models.Model):
    _name = 'life.insurance.enrollment'
    _description = 'Life Insurance Enrollment'

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
        ('activated', 'Activated'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    employee_id = fields.Many2one('hr.employee',string="Employee",required=True,domain="[('client_parent_id','=',client_parent_id)]")
    iqama_no = fields.Char(string="Iqama No",copy=False)

    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",required=True)


    passport_copy = fields.Binary(string="Passport")
    other_document = fields.Binary(string="Other Document")
    confirmation_of_activation_doc = fields.Binary(string="Confirmation of Activation Document")

    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')

    @api.onchange('employee_id')
    def onchange_employee_details(self):
    	for line in self:
    		line.iqama_no = line.employee_id.iqama_no
    		line.passport_copy = line.employee_id.passport_copy


    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('life.insurance.enrollment')
        res = super(LifeInsuranceEnrollment,self).create(vals_list)
        return res

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def action_submit(self):
        for line in self:
            line.state = 'submitted'

    def action_confirm_activation(self):
        for line in self:
            if not self.confirmation_of_activation_doc:
                raise UserError('Upload Confirmation of Activation Document.')
            line.state = 'activated'


    def action_done(self):
        for line in self:
            line.state = 'done'

