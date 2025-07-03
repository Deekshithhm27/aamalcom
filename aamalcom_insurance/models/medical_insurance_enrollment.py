from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

class MedicalInsuranceEnrollment(models.Model):
    _name = 'medical.insurance.enrollment'
    _description = 'Medical Insurance Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

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
            res['draft_hdf_form'] = hdf_form_record.hdf_form
        return res

    name = fields.Char(string="Reference",copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('review_to_be_done', 'Review to be Done - PM'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]",tracking=True)
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    enrollment_type = fields.Selection([('employee','Employee'),('dependents','Employee Dependents'),('work_visit_visa','Work Visit Visa')],string="Enrollment Type",default="employee",tracking=True)
    employee_id = fields.Many2one('hr.employee',string="Employee",required=True,domain="[('client_parent_id','=',client_parent_id)]",tracking=True)
    work_phone = fields.Char(string="Phone No.",tracking=True)
    gender = fields.Selection([('male','Male'),('female','Female'),('others','Others')],string="Gender",tracking=True)


    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",required=True,tracking=True)

    membership_number = fields.Char(string="Membership Number",tracking=True)

    dependent_name = fields.Char(string='Dependent Name',tracking=True)

    is_inside_ksa = fields.Boolean(string="Born - Inside KSA",
                                    help="Indicates whether the employee is Inside KSA (True)",tracking=True)
    is_outside_ksa = fields.Boolean(string="Born - Outside KSA",
                                    help="Indicates whether the employee is Outside KSA (True)",tracking=True)

    draft_hdf_form = fields.Binary(string="Draft HDF Form")

    hdf_form = fields.Binary(string="HDF Form")
    hdf_form_filename = fields.Char(string="HDF Form File name")

    passport_copy = fields.Binary(string="Passport")
    passport_copy_filename = fields.Char(string="Passport Filename")
    passport_copy_ref = fields.Char(string="Ref No*", tracking=True)

    issued_visa = fields.Binary(string="Issued Visa")
    issued_visa_filename = fields.Char(string="Issued Visa Filename")
    visa_ref = fields.Char(string="Ref No*",tracking=True)

    dependent_passport_copy = fields.Binary(string="Passport Document")
    dependent_passport_copy_filename = fields.Char("Passport Filename")
    dependent_passport_copy_ref = fields.Char(string="Ref No*", tracking=True)

    dependent_birth_certificate = fields.Binary(string="Birth Certificate Document")
    dependent_birth_certificate_filename = fields.Char("Birth Certificate Filename")
    dependent_birth_certificate_ref = fields.Char(string="Ref No*", tracking=True)

    absher_with_border_doc = fields.Binary(string="Absher with Border Number")
    absher_with_border_doc_filename = fields.Char("Absher Document Filename")
    absher_with_border_doc_ref = fields.Char(string="Ref No*", tracking=True)

    dependent_visa_doc = fields.Binary(string="Visa Document")
    dependent_visa_doc_filename = fields.Char("Visa Document Filename")
    dependent_visa_doc_ref = fields.Char(string="Ref No*", tracking=True)

    cchi_confirmation_document = fields.Binary(string="CCHI Confirmation Document")
    cchi_filename = fields.Char(string="CCHI Filename")
    cchi_ref = fields.Char(string="Ref No*")

    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')

    iqama_no = fields.Char(string="Iqama No.",tracking=True)
    identification_id = fields.Char(string="Border No.",tracking=True)
    passport_no = fields.Char(string='Passport no',tracking=True)
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Number",tracking=True)

    @api.onchange('employee_id')
    def onchange_employee_details(self):
        for line in self:
            line.work_phone = line.employee_id.work_phone
            line.gender = line.employee_id.gender
            line.passport_copy = line.employee_id.passport_copy
            line.iqama_no = line.employee_id.iqama_no
            line.identification_id = line.employee_id.identification_id
            line.passport_no = line.employee_id.passport_id
            line.sponsor_id = line.employee_id.sponsor_id.id

    @api.onchange('enrollment_type')
    def employee_filter_work_visa(self):
        for line in self:
            if line.enrollment_type =='work_visit_visa':
                return {'domain': {'service_enquiry_id': [('service_request', '=', 'final_exit_issuance'),('employee_id','=',self.employee_id.id)]}}


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
            # Always required
            required_fields = [
                ('hdf_form', "Kindly Upload HDF Form"),
            ]

            if line.enrollment_type in ('employee', 'work_visit_visa'):
                required_fields += [
                    ('issued_visa', "Kindly Upload Issued Visa"),
                    ('visa_ref', "Kindly Update Reference for Issued Visa"),
                    ('passport_copy', "Kindly Upload Passport Copy"),
                    ('passport_copy_ref', "Kindly Update Reference for Passport Copy"),
                ]

            elif line.enrollment_type == 'dependents':
                required_fields += [
                    ('dependent_passport_copy', "Kindly Upload Passport Copy"),
                    ('dependent_passport_copy_ref', "Kindly Update Reference for Passport Copy"),
                ]
                if line.is_inside_ksa:
                    required_fields += [
                        ('dependent_birth_certificate', "Kindly Upload Birth Certificate"),
                        ('dependent_birth_certificate_ref', "Kindly Update Reference for Birth Certificate"),
                    ]
                if line.is_outside_ksa:
                    required_fields += [
                        ('absher_with_border_doc', "Kindly Upload Absher with Border Number"),
                        ('absher_with_border_doc_ref', "Kindly Update Reference for Absher with Border Number"),
                        ('dependent_visa_doc', "Kindly Upload Visa Document"),
                        ('dependent_visa_doc_ref', "Kindly Update Reference for Visa Document"),
                    ]


            # Validate all required fields
            for field_name, error_msg in required_fields:
                if not getattr(line, field_name):
                    raise ValidationError(error_msg)

            if not line.is_inside_ksa and not line.is_outside_ksa and line.enrollment_type == 'dependents':
                raise ValidationError("Choose whether dependent is Born Inside or Outside KSA")


            line.state = 'submitted'

    def action_submit_to_review(self):
        for line in self:
            if not self.cchi_confirmation_document:
                raise UserError('Upload CCHI Confirmation Document.')
            if not self.cchi_ref:
                raise UserError('Kindly update Reference for CCHI Confirmation Document.')
            line.state = 'review_to_be_done'


    def action_done(self):
        for line in self:
            if line.employee_id:
                if line.enrollment_type == 'employee':
                    line.employee_id.member_no = line.membership_number
                if line.enrollment_type == 'dependents':
                    dependent_name = line.dependent_name.strip() if line.dependent_name else ''
                    if not dependent_name:
                        raise ValidationError("Dependent name is required to update dependent record.")

                    # Search for existing dependent by name
                    existing_dependent = line.employee_id.dependent_ids.filtered(
                        lambda dep: dep.name.strip().lower() == dependent_name.lower()
                    )

                    if existing_dependent:
                        # Update existing dependent's member number
                        existing_dependent.member_no = line.membership_number
                    else:
                        # Create a new dependent record
                        self.env['employee.dependents'].create({
                            'employee_id': line.employee_id.id,
                            'name': dependent_name,
                            'member_id': line.membership_number,
                        })
            line.state = 'done'

    @api.constrains(
        'hdf_form', 'hdf_form_filename',
        'passport_copy', 'passport_copy_filename',
        'issued_visa', 'issued_visa_filename',
        'dependent_passport_copy', 'dependent_passport_copy_filename',
        'dependent_birth_certificate', 'dependent_birth_certificate_filename',
        'absher_with_border_doc', 'absher_with_border_doc_filename',
        'dependent_visa_doc', 'dependent_visa_doc_filename',
    )
    def _check_documents_are_pdf(self):
        pdf_fields = [
            ('hdf_form', 'hdf_form_filename', 'HDF Form'),
            ('passport_copy', 'passport_copy_filename', 'Passport Copy'),
            ('issued_visa', 'issued_visa_filename', 'Issued Visa'),
            ('dependent_passport_copy', 'dependent_passport_copy_filename', 'Dependent Passport Copy'),
            ('dependent_birth_certificate', 'dependent_birth_certificate_filename', 'Birth Certificate'),
            ('absher_with_border_doc', 'absher_with_border_doc_filename', 'Absher with Border Number'),
            ('dependent_visa_doc', 'dependent_visa_doc_filename', 'Dependent Visa'),
            ('cchi_confirmation_document','cchi_filename', 'CCHI Confirmation')
        ]

        for rec in self:
            for binary_field, filename_field, label in pdf_fields:
                binary = getattr(rec, binary_field)
                filename = getattr(rec, filename_field)
                if binary and filename:
                    if not filename.lower().endswith('.pdf'):
                        raise ValidationError(f"{label} must be a PDF file.")

    