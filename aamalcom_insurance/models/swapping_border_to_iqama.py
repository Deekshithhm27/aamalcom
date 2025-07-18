# File: aamalcom_insurance/models/medical_insurance_deletion.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

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
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,domain="[('client_parent_id','=',client_parent_id)]",tracking=True)
    service_enquiry_id = fields.Many2one('service.enquiry', string='Service Enquiry',tracking=True)
    project_manager_id = fields.Many2one('hr.employee',string="Project Manager")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('review_to_be_done', 'Review to be Done - PM'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)

    swapping_type = fields.Selection([('employee','Employee'),('dependents','Employee Dependents')],string="Swapping Type",default="employee",tracking=True)

    digital_iqama_copy = fields.Binary(string="Digital Iqama Copy")
    digital_iqama_copy_filename = fields.Char(string="Digital Iqama Filename")
    digital_iqama_copy_ref = fields.Char(string="Ref No *", tracking=True)

    cchi_confirmation_document = fields.Binary(string="CCHI Confirmation Document")
    cchi_confirmation_document_filename = fields.Char(string="CCHI Confirmation Filename")
    cchi_confirmation_document_ref = fields.Char(string="Ref No*", tracking=True)

    residance_doc = fields.Binary(string="Residance Doc")
    residance_doc_filename = fields.Char(string="Residance Doc Filename")
    residance_doc_ref = fields.Char(string="Ref No *", tracking=True)

    muqeem_print_doc = fields.Binary(string="Muqeem Print Doc")
    muqeem_print_doc_filename = fields.Char(string="Muqeem Print Filename")
    muqeem_print_doc_ref = fields.Char(string="Ref No *", tracking=True)

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
            if line.swapping_type == "employee":
                required_fields = [
                    ('residance_doc', "Kindly Upload Residance Document"),
                    ('muqeem_print_doc',"Kindly Upload Muqeem Document")
                ]
                # Validate all required fields
                for field_name, error_msg in required_fields:
                    if not getattr(line, field_name):
                        raise ValidationError(error_msg)
                if not line.residance_doc_ref:
                    raise ValidationError("Kindly Update Reference for Residance Document")
                if not line.muqeem_print_doc_ref:
                    raise ValidationError("Kindly Update Reference for Muqeem Document")
            if line.swapping_type == "dependents":
                required_fields = [
                    ('digital_iqama_copy', "Kindly Upload Digital Iqama Copy"),
                ]
                # Validate all required fields
                for field_name, error_msg in required_fields:
                    if not getattr(line, field_name):
                        raise ValidationError(error_msg)
                if not line.digital_iqama_copy_ref:
                    raise ValidationError("Kindly Update Reference for Digital Iqama Copy")

            line.state = 'submitted'

    def action_submit_to_review(self):
        for line in self:
            if not self.cchi_confirmation_document:
                raise UserError('Upload CCHI Confirmation Document.')
            if not self.cchi_confirmation_document_ref:
                raise UserError("Kindly Update Reference for CCHI Confirmation Document")
            line.state = 'review_to_be_done'


    def action_done(self):
        for line in self:
            line.state = 'done'


    @api.constrains(
        'digital_iqama_copy', 'digital_iqama_copy_filename',
        'cchi_confirmation_document', 'cchi_confirmation_document_filename',
        'residance_doc', 'residance_doc_filename',
        'muqeem_print_doc', 'muqeem_print_doc_filename',
    )
    def _check_documents_are_pdf_format(self):
        file_pairs = [
            ('digital_iqama_copy', 'digital_iqama_copy_filename', 'Digital Iqama Copy'),
            ('cchi_confirmation_document', 'cchi_confirmation_document_filename', 'CCHI Confirmation Document'),
            ('residance_doc', 'residance_doc_filename', 'Residance Doc'),
            ('muqeem_print_doc', 'muqeem_print_doc_filename', 'Muqeem Print Doc'),
        ]

        for rec in self:
            for binary_field, filename_field, label in file_pairs:
                binary = getattr(rec, binary_field)
                filename = getattr(rec, filename_field)
                if binary and filename and not filename.lower().endswith('.pdf'):
                    raise ValidationError(f"{label} must be uploaded as a PDF file.")
