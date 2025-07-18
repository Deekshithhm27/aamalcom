from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class LifeInsuranceEnrollment(models.Model):
    _name = 'life.insurance.enrollment'
    _description = 'Life Insurance Enrollment'
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
        ('activated', 'Activated'),
        ('review_to_be_done', 'Review to be Done - PM'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]",tracking=True)
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    employee_id = fields.Many2one('hr.employee',string="Employee",required=True,domain="[('client_parent_id','=',client_parent_id)]")
    iqama_no = fields.Char(string="Iqama No",copy=False,tracking=True)
    identification_id = fields.Char(string="Border No.",tracking=True)
    passport_no = fields.Char(string='Passport no',tracking=True)
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Number",tracking=True)

    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_silver+','SILVER+'),('class_silver','SILVER'),('class_a+','A+'),('class_a','A'),('class_b+','B+'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",required=True,tracking=True)


    passport_copy = fields.Binary(string="Passport")
    passport_copy_filename = fields.Char(string="Passport Filename")
    passport_copy_ref = fields.Char(string="Ref No *", tracking=True)

    iqama_doc = fields.Binary(string="Iqama Document")
    iqama_doc_filename = fields.Char(string="Iqama Filename")
    iqama_doc_ref = fields.Char(string="Ref No*", tracking=True)

    other_document = fields.Binary(string="Other Document")
    other_document_filename = fields.Char(string="Other Document Filename")
    other_document_ref = fields.Char(string="Ref No", tracking=True)

    confirmation_of_activation_doc = fields.Binary(string="Document - Confirmation of Activation")
    confirmation_of_activation_doc_filename = fields.Char(string="Confirmation Doc Filename")
    confirmation_of_activation_doc_ref = fields.Char(string="Ref No *", tracking=True)

    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')

    @api.onchange('employee_id')
    def onchange_employee_details(self):
        for line in self:
            line.iqama_no = line.employee_id.iqama_no
            line.passport_copy = line.employee_id.passport_copy
            line.identification_id = line.employee_id.identification_id
            line.passport_no = line.employee_id.passport_id
            line.sponsor_id = line.employee_id.sponsor_id.id



    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('life.insurance.enrollment')
        res = super(LifeInsuranceEnrollment,self).create(vals)
        return res

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def action_submit(self):
        for line in self:
            required_fields = [
                ('passport_copy', "Kindly Upload Passport Copy"),
                ('iqama_doc', "Kindly Upload Iqama Document"),
            ]
            for field_name, error_msg in required_fields:
                if not getattr(line, field_name):
                    raise ValidationError(error_msg)
            if not line.passport_copy_ref:
                raise ValidationError("Kindly update Reference for Passport Copy")
            if not line.iqama_doc_ref:
                raise ValidationError("Kindly update Reference for Iqama Document")
            line.state = 'submitted'

    def action_confirm_activation(self):
        for line in self:
            if not self.confirmation_of_activation_doc:
                raise UserError('Upload Confirmation of Activation Document.')
            if not self.confirmation_of_activation_doc_ref:
                raise UserError('Kindly update Reference for Confirmation of Activation Document.')
            line.state = 'activated'


    def action_done(self):
        for line in self:
            line.state = 'done'

    def action_submit_to_review(self):
        for line in self:
            line.state = 'review_to_be_done'


    @api.constrains(
        'passport_copy', 'passport_copy_filename',
        'iqama_doc', 'iqama_doc_filename',
        'other_document', 'other_document_filename',
        'confirmation_of_activation_doc', 'confirmation_of_activation_doc_filename',
    )
    def _check_uploaded_docs_are_pdf(self):
        doc_fields = [
            ('passport_copy', 'passport_copy_filename', 'Passport'),
            ('iqama_doc', 'iqama_doc_filename', 'Iqama Document'),
            ('other_document', 'other_document_filename', 'Other Document'),
            ('confirmation_of_activation_doc', 'confirmation_of_activation_doc_filename', 'Confirmation of Activation'),
        ]

        for rec in self:
            for binary_field, filename_field, label in doc_fields:
                binary = getattr(rec, binary_field)
                filename = getattr(rec, filename_field)
                if binary and filename and not filename.lower().endswith('.pdf'):
                    raise ValidationError(f"{label} must be uploaded as a PDF file.")

