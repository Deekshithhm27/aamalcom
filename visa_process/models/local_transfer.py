# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class LocalTransfer(models.Model):
    _name = 'local.transfer'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Local Transfer"


    
    name = fields.Char(string="Sequence",help="The Unique Sequence no", readonly=True, default='/')

    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)
    client_id = fields.Many2one('res.partner',string="Client Spoc",default=lambda self: self.env.user.partner_id)
    client_company_id = fields.Many2one('res.partner',string="Client",default=lambda self: self.env.user.partner_id.parent_id)
    approver_id = fields.Many2one('hr.employee',string="Approver")

    employee_id = fields.Many2one('hr.employee',domain="[('custom_employee_type', '=', 'external'),('service_request_type','=','lt_request'),('client_id','=',user_id)]",string="Employee name (as per Passport)",tracking=True,required=True)
    birthday = fields.Date(string="Date of Birth *",tracking=True)
    contact_no = fields.Char(string="Cell No. (Absher) *")
    private_email = fields.Char(string="Email Id *",tracking=True)
    country_id = fields.Many2one('res.country',string="Nationality",tracking=True)
    phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
    iqama_no = fields.Char(string="Iqama No *")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting for Approval'),('approved','Approved'),('reject','Rejected'),('cancel','Cancel')], string='State',default="draft",copy=False,tracking=True)

    # Employment details
    doj = fields.Date(string="Projected Date of Joining",tracking=True)
    employment_duration = fields.Many2one('employment.duration',string="Duration of Employment *",tracking=True)
    working_days = fields.Char(string="Working Days *")
    working_hours = fields.Char(string="Working Hours *")
    annual_vacation = fields.Char(string="Annual Vacation *")

    
    

    # # Documents
    passport_size_photo = fields.Binary(string="Passport Size Photo")
    passport_copy = fields.Binary(string="Passport Copy *")
    dependents_if_any = fields.Binary(string="Dependents if any")
    signed_offer_letter = fields.Binary(string="Signed Offer Letter *")
    bank_iban_letter = fields.Binary(string="Bank Iban Letter *")
    self_iqama = fields.Binary(string="Iqama *")
    certificate_1 = fields.Binary(string="Certificates *")
    certificate_2 = fields.Binary(string="Certificates")
    other_doc_1 = fields.Binary(string="Others")
    other_doc_2 = fields.Binary(string="Others")
    other_doc_3 = fields.Binary(string="Others")
    other_doc_4 = fields.Binary(string="Others")
    

    

    # Profession Details
    profession_en = fields.Char(string="Profession En.")
    profession_arabic = fields.Char(string="Profession Ar.")
    qualification = fields.Char(string="Education Qualification *")

    iqama = fields.Char(string="Designation on Iqama *")
    expiry_date = fields.Date(string="Expiry Date")
    
    work_location_id = fields.Many2one('hr.work.location',string="Work Location",tracking=True)

    # Air Fare
    air_fare_for = fields.Selection([('self','Self'),('family','Family')],string="Air Fare for?")
    air_fare_frequency = fields.Char(string="Air Fare Frequency")

    # Medical Insurance
    medical_insurance_for = fields.Selection([('self','Self'),('family','Family'),('both','Both')],string="Medical Insurance For?")
    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Class *")
    dependent_document_ids = fields.One2many('dependent.documents','lt_dependent_document_id',string="Dependent Documents")

    # Bank details
    bank_id = fields.Many2one('res.bank', string="Bank *",tracking=True)
    bic = fields.Char(string="IBAN *",tracking=True)

    notes = fields.Text(string="Notes")

    @api.onchange('employee_id')
    def onchange_employee_update_data(self):
        for line in self:
            if line.employee_id:
                line.country_id = line.employee_id.country_id
                line.private_email = line.employee_id.private_email
                line.marital = line.employee_id.marital
                line.employment_duration = line.employee_id.employment_duration
                line.doj = line.employee_id.doj
                line.work_location_id = line.employee_id.work_location_id
                line.birthday = line.employee_id.birthday
                line.profession_en = line.employee_id.iqama
                line.iqama = line.employee_id.iqama
                line.working_days = line.employee_id.working_days


    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for objects in self:
            if objects.state in ['waiting', 'approved', 'rejected']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(LocalTransfer, self).unlink()

    

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('local.transfer')
        res = super(LocalTransfer,self).create(vals_list)
        return res

    def _add_followers(self):
        """
            Add Approver as followers
        """
        partner_ids = []
        if self.approver_id:
            partner_ids.append(self.approver_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def action_submit(self):
        # categ_ids = [x.id for x in list(self.category_id)]
        # preffered_location_ids = [x.id for x in list(self.preffered_location_id)]
        
        date = fields.Date.today()
        
        # vals = {
        #     'client_id': self.client_id.id,
        #     'service_req_id': self.id,
        #     'employee_id':self.employee_id.id,
        #     # 'category_id':[(6, 0, categ_ids)],
        #     # 'preffered_location_id':[(6, 0, preffered_location_ids)],
        #     'designation':self.designation,
        #     'salary_line_ids':[(6, 0, [salary.id for salary in self.salary_line_ids])],
        #     'document_line_ids':[(6, 0, [doc.id for doc in self.document_line_ids])],
        #     'doj':self.doj,
        #     'employment_duration':self.employment_duration.id,
        #     'probation_term':self.probation_term,
        #     'notice_period':self.notice_period,
        #     'weekly_off_days':self.weekly_off_days,
        #     'service_request_type_id':self.service_request_type_id.id,
        #     'document_creation_date':date,
        #     'approver_id':self.client_id.company_spoc_id.id,
        # }
        # service_request_approval_id = self.env['local.transfer.approval'].sudo().create(vals)
        if not self.employment_duration:
            raise UserError(_('Please add Duration of Employment!'))
        if not self.qualification:
            raise UserError(_('Please add Education Qualification!'))
        if not self.private_email:
            raise UserError(_("Please add Email Id"))
        if not self.signed_offer_letter:
            raise UserError(_("Please attach signed offer letter"))
        if not self.passport_copy:
            raise UserError(_("Please attach Passport Copy"))
        if not self.birthday:
            raise UserError(_("Please add Birth date"))
        if not self.working_days:
            raise UserError(_("Please add Working Days"))
        if not self.working_hours:
            raise UserError(_("Please add Working Hours"))
        if not self.annual_vacation:
            raise UserError(_("Please add Annual Vacation"))
        if not self.bank_id:
            raise UserError(_("Please add Bank"))
        if not self.bic:
            raise UserError(_("Please add IBAN"))
        if not self.bank_iban_letter:
            raise UserError(_("Please attach Bank Iban Letter"))
        if not self.certificate_1:
            raise UserError(_("Please attach Certificate"))
        if not self.insurance_class:
            raise UserError(_("Please select medical Insurance class"))
        if not self.contact_no:
            raise UserError(_("Please Add Cell No. (Absher)"))
        if not self.iqama:
            raise UserError(_("Please Add Designation on Iqama"))
        if not self.iqama_no:
            raise UserError(_("Please Provide Iqama No"))


        self._add_followers()
        self.approver_id = self.client_id.company_spoc_id.id 
        self.state = 'waiting'

    def action_approve(self):
        for line in self:
            line.state = 'approved'

    def action_reject(self):
        for line in self:
            line.state = 'reject'


    def action_cancel(self):
        for line in self:
            line.state = 'cancel'
