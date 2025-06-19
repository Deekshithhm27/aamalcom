# File: aamalcom_insurance/models/medical_insurance_deletion.py
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MedicalInsuranceDeletion(models.Model):
    _name = 'medical.insurance.deletion'
    _description = 'Medical Insurance Deletion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        group_pm = self.env.ref('visa_process.group_service_request_manager')
        if group_pm:
            res['is_pm_user'] = True
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
        return res
    name = fields.Char(string='Request Reference', copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",domain="[('is_company','=',True),('parent_id','=',False)]")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,domain="[('client_parent_id','=',client_parent_id)]")
    service_enquiry_id = fields.Many2one('service.enquiry', string='Service Enquiry')
    is_pm_user = fields.Boolean(string="Is PM User")
    govt_user_id = fields.Many2one('res.users',string="Govt Employee")



    deletion_type = fields.Selection([
        ('final_exit', 'Final Exit'),
        ('iqama_transfer', 'Iqama Transfer to Another Establishment'),
        ('absconding', 'Absconding'),
        ('not_returned', 'Exit but Not Returned to KSA')
    ], string='Deletion Type', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('sent_govt_confirmation', 'Sent for Govt Team Confirmation'),
        ('govt_confirmation_received', 'Govt Team Confirmation Received'),
        ('pm_confirmation', 'PM Confirmed'),
        ('insurance_upload', 'Insurance Upload'),
        ('done', 'Completed')
    ], string='Status', default='draft', tracking=True)


    is_inside_ksa = fields.Boolean(string="Inside KSA",
                                    help="Indicates whether the employee is Inside KSA (True)")
    is_outside_ksa = fields.Boolean(string="Outside KSA",
                                    help="Indicates whether the employee is Outside KSA (True)")
    exit_stamp = fields.Binary(string='Exit Stamp')
    muqeem_report = fields.Binary(string='Muqeem Report')
    absconding_muqeem_report = fields.Binary(string='Absconding Muqeem Report')
    not_returned_muqeem_report = fields.Binary(string='Exit but not returned Muqeem Report')

    confirmed_by_pm = fields.Many2one('res.users', string='Confirmed by PM', readonly=True)
    confirmed_by_insurance = fields.Many2one('res.users', string='Confirmed by Insurance', readonly=True)

    insurance_document = fields.Binary(string="Insurance Deletion Document")
    is_insurance_user = fields.Boolean(string="Is Insurance User", compute='_compute_is_insurance_user')
    is_govt_user = fields.Boolean(string="Is Govt User", compute='_compute_is_govt_user')

    def _compute_is_insurance_user(self):
        group = self.env.ref('visa_process.group_service_request_insurance_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_insurance_user = is_user

    def _compute_is_govt_user(self):
        group = self.env.ref('visa_process.group_service_request_employee')
        is_user = group in self.env.user.groups_id
        for rec in self:
            rec.is_govt_user = is_user



    @api.onchange('is_outside_ksa')
    def update_in_ksa_status(self):
        for line in self:
            if line.is_outside_ksa == True:
                line.is_inside_ksa = False

    @api.onchange('is_inside_ksa')
    def update_out_ksa_status(self):
        for line in self:
            if line.is_inside_ksa == True:
                line.is_outside_ksa = False

    @api.onchange('deletion_type','employee_id')
    def _onchange_deletion_type(self):
        if self.deletion_type == 'final_exit':
            return {'domain': {'service_enquiry_id': [('service_request', '=', 'final_exit_issuance'),('employee_id','=',self.employee_id.id)]}}
        elif self.deletion_type == 'iqama_transfer':
            return {'domain': {'service_enquiry_id': [('service_request', '=', 'transfer_req'),('transfer_type','=','to_another_establishment'),('employee_id','=',self.employee_id.id)]}}
        else:
            self.service_enquiry_id = False
            return {'domain': {'service_enquiry_id': [('id', '=', 0)]}}


    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.insurance.deletion')
        res = super(MedicalInsuranceDeletion,self).create(vals_list)
        return res

    def action_submit(self):
        self.ensure_one()
        if self.deletion_type in ('final_exit','absconding','not_returned'):
            self.state = 'submitted'
        if self.deletion_type == 'iqama_transfer':
            self.state = 'insurance_upload'

    def action_get_confirmation(self):
        self.ensure_one()
        self.state = 'sent_govt_confirmation'

    def action_govt_confirm(self):
        self.ensure_one()
        # if not self.env.user.has_group('visa_process.group_service_request_employee'):
        #     raise UserError('You are not authorized to confirm as Govt team.')
        self.govt_user_id = self.env.user.id
        self.state = 'govt_confirmation_received'

    def action_pm_confirm_exit(self):
        self.ensure_one()
        # if not self.env.user.has_group('visa_process.group_service_request_manager'):
        #     raise UserError('Only Project Manager can perform this action.')
        self.confirmed_by_pm = self.env.user.id
        self.state = 'pm_confirmation'

    def action_insurance_confirm(self):
        self.ensure_one()
        # if not self.env.user.has_group('visa_process.group_service_request_insurance_employee'):
        #     raise UserError('Only Insurance team can perform this action.')
        if not self.insurance_document and self.deletion_type in ('iqama_transfer','absconding','not_returned'):
            raise UserError('Upload Insurance Deletion document before confirmation.')
        self.confirmed_by_insurance = self.env.user.id
        self.state = 'done'

    def action_docs_uploaded(self):
        self.ensure_one()
        if self.deletion_type == 'final_exit' and (not self.exit_stamp or not self.muqeem_report):
            raise UserError('Upload required documents before confirmation.')
        if not self.absconding_muqeem_report and self.deletion_type == 'absconding':
            raise UserError('Upload Absconding Muqeem Document before confirmation.')
        if not self.not_returned_muqeem_report and self.deletion_type == 'not_returned':
            raise UserError('Upload Exit but not returned Muqeem Document before confirmation.')
        if self.env.user.has_group('visa_process.group_service_request_employee'):
            self.govt_user_id = self.env.user.id
        self.state = 'insurance_upload'