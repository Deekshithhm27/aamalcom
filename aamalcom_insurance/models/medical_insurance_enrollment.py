from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class MedicalInsuranceEnrollment(models.Model):
    _name = 'medical.insurance.enrollment'
    _description = 'Life Insurance Enrollment'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
            res['project_manager_id'] = self.env.user.partner_id.company_spoc_id.id
        # default load form
        hdf_form_record = self.env['hdf.form'].search(
            [('name', '=', 'Medical Enrollment HDF Form')], limit=1
        )
        if hdf_form_record:
            res['hdf_form'] = hdf_form_record.hdf_form
        return res

    name = fields.Char(string="Reference",copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('review_to_be_done', 'Review to be Done'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    enrollment_type = fields.Selection([('employee','Employee'),('dependents','Employee Dependents'),('work_visit_visa','Work Visit Visa')],string="Enrollment Type",default="employee")
    employee_id = fields.Many2one('hr.employee',string="Employee",required=True,domain="[('client_parent_id','=',client_parent_id)]")
    work_phone = fields.Char(string="Phone No.")
    gender = fields.Selection([('male','Male'),('female','Female'),('others','Others')],string="Gender")



    passport_copy = fields.Binary(string="Passport")
    issued_visa = fields.Binary(string="Issued Visa")
    visa_ref = fields.Char(string="Ref No*")

    hdf_form = fields.Binary(string="HDF Form")
    hdf_form_ref = fields.Char(string="Ref No*")

    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",required=True)

    cchi_confirmation_document = fields.Binary(string="CCHI Confirmation Document")
    membership_number = fields.Char(string="Membership Number")

    dependent_name = fields.Char(string='Dependent Name')

    is_inside_ksa = fields.Boolean(string="Born - Inside KSA",
                                    help="Indicates whether the employee is Inside KSA (True)")
    is_outside_ksa = fields.Boolean(string="Born - Outside KSA",
                                    help="Indicates whether the employee is Outside KSA (True)")

    dependent_passport_copy = fields.Binary(string="Passport Document")
    dependent_birth_certificate = fields.Binary(string="Birth Certificate Document")
    absher_with_border_doc = fields.Binary(string="Absher with Border Number")
    dependent_visa_doc = fields.Binary(string="Visa Document")

    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')

    @api.onchange('employee_id')
    def onchange_employee_details(self):
        for line in self:
            line.work_phone = line.employee_id.work_phone
            line.gender = line.employee_id.gender
            line.passport_copy = line.employee_id.passport_copy

    @api.onchange('is_outside_ksa')
    def update_in_ksa_status(self):
        for line in self:
            if line.is_outside_ksa == True:
                line.is_inside_ksa = False
                line.dependent_birth_certificate = False

    @api.onchange('is_inside_ksa')
    def update_out_ksa_status(self):
        for line in self:
            if line.is_inside_ksa == True:
                line.is_outside_ksa = False
                line.absher_with_border_doc = False
                line.dependent_visa_doc = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.insurance.enrollment')
        res = super(MedicalInsuranceEnrollment,self).create(vals)
        return res

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def action_submit(self):
        for line in self:
            # if not line.hdf_form_ref:
            #     raise ValidationError("Kindly Update Reference Number for HDF Form")
            # if not line.visa_ref:
            #     raise ValidationError("Kindly Update Reference Number for Issued Visa")

            line.state = 'submitted'

    def action_submit_to_review(self):
        for line in self:
            if not self.cchi_confirmation_document:
                raise UserError('Upload CCHI Confirmation Document.')
            line.state = 'review_to_be_done'


    def action_done(self):
        for line in self:
            if line.employee_id:
                if line.enrollment_type == 'employee':
                    line.employee_id.member_no = line.membership_number
            line.state = 'done'

