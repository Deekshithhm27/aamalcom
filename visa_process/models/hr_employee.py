# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sequence = fields.Char(string="Sequence",help="The Unique Sequence no", readonly=True, default='/')

    client_emp_sequence = fields.Char(string="Employee Id",help="Employee Id as per client database")
    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa'),('twv_request','Temporary Work Visa')],string="Service Request Type",tracking=True)
    hr_employee_company_id = fields.Many2one('hr.employee.company',string="Company",help="This field is used to tag the employee of different sister company")
    identification_id = fields.Char(string='Border No.', groups="hr.group_hr_user", tracking=True)
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Number",tracking=True,copy=False)
    req_completion_date = fields.Datetime(string="Request Completion Date",copy=False)
    
    surname = fields.Char(string="Surname",tracking=True)
    given_name = fields.Char(string="Given Name",tracking=True)
    # replaced to birthday
    # nationality_id = fields.Many2one('res.country',string="Nationality",tracking=True)
    # replaces to country id
    
    
    contact_no = fields.Char(string="Contact # in the country")
    phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")
    arrival_date = fields.Date(string='Arrival Date')

    current_contact = fields.Char(string="Current Contact # (if Outside the country)")
    current_phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")

    religion = fields.Selection([('muslim','Muslim'),('non_muslim','Non-Muslim'),('others','Others')],string="Religion")

    client_id = fields.Many2one('res.users',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client",related="client_id.partner_id.parent_id",store=True)
    company_spoc_id = fields.Many2one('hr.employee',string="Project Manager",tracking=True,compute="update_project_manager",store=True)


    passport_copy = fields.Binary(string="Passport")
    degree_certificate = fields.Binary(string="Degree")
    qiwa_contract_doc = fields.Binary(string="Qiwa Contract")
    qiwa_contract_doc_name = fields.Char(string="Qiwa Contract File Name")
    qiwa_contract_sr_no = fields.Char(string="Qiwa Contract Reference ID", readonly=True)
    qiwa_contract_ref_no = fields.Char(string="Ref NO.*")
    
    work_address = fields.Char(string="Work Address")
    personal_address = fields.Char(string="Persoanl Address")
    
    doj = fields.Date(string="Projected Date of Joining",tracking=True)

    # employment_duration = fields.Many2one('employment.duration',string="Duration of Employment",tracking=True)
    employment_duration = fields.Selection([('3','3 Months'),('6','6 Months'),('9','9 Months'),('12','12 Months'),
        ('15','15 Months'),('18','18 Months'),('21','21 Months'),('24','24 Months')],string="Duration of Employment",tracking=True)
    probation_term = fields.Char(string="Probation Term")

    probation_end_date = fields.Date(
        string="Probation End Date",
        compute='_compute_probation_end_date',
    )
    notice_period = fields.Char(string="Notice Period")
    working_days = fields.Char(string="Working Days")
    weekly_off_days = fields.Char(string="Weekly Off (No. Of Days)")
    

    work_location = fields.Char(string="Work Location")
    

    iqama = fields.Char(string="Designation on Iqama")
    iqama_no = fields.Char(string="Iqama No",copy=False)

    # This field is to differentiate between internal and external (client) employees
    custom_employee_type = fields.Selection([('external','External'),('internal','Internal')],string="Type of user to set System Access",default=lambda self: self.env.user.user_type)
    # below field was overrided from standard and added group
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user,visa_process.group_hr_employee,visa_process.group_hr_client", copy=False)
    first_contract_date = fields.Date(compute='_compute_first_contract_date', groups="hr.group_hr_user,visa_process.group_hr_employee,visa_process.group_hr_client", store=True)
    contract_warning = fields.Boolean(string='Contract Warning', store=True, compute='_compute_contract_warning', groups="hr.group_hr_user,visa_process.group_hr_employee,visa_process.group_hr_client")

    hr_agency_id = fields.Many2one('hr.agency',string="Agency")
    country_of_birth = fields.Many2one('res.country', string="Issuance of Passport - Country", groups="hr.group_hr_user", tracking=True)
    passport_issuance_city = fields.Char(string="Issuance of Passport - City")

    member_no = fields.Char(string="Insurance Member Number")

    bank_ids = fields.One2many('res.partner.bank','employee_id',string="Banks")
    job_description = fields.Text(string="Job Description")
    can_edit_job_description = fields.Boolean(
        compute="_compute_can_edit_job_description",
        string="Can Edit Job Description",
        store=False
    )

    @api.depends('custom_employee_type') # Added custom_employee_type to dependencies
    def _compute_can_edit_job_description(self):
        """Check if user belongs to the correct group based on employee type."""
        manager_group = "visa_process.group_service_request_manager"
        client_spoc_group = "visa_process.group_service_request_client_spoc"
        hr_manager_group = "visa_process.group_service_request_hr_manager"
        
        # Pre-fetch user's group status outside the loop for efficiency
        is_manager = self.env.user.has_group(manager_group)
        is_client_spoc = self.env.user.has_group(client_spoc_group)
        is_hr_manager = self.env.user.has_group(hr_manager_group)

        for rec in self:
            can_edit = False
            if rec.custom_employee_type == 'external':
                # Editable by service_request_manager OR service_request_client_spoc
                if is_manager or is_client_spoc:
                    can_edit = True
            elif rec.custom_employee_type == 'internal':
                # Editable by service_request_hr_manager
                if is_hr_manager:
                    can_edit = True
            
            rec.can_edit_job_description = can_edit
    ##To track who edited the job description 
    def write(self, vals):
        """ Log an update to the Job Description field """
        
        if 'job_description' in vals:
            for employee in self: # 'employee' is a single record
                old_description = employee.job_description or ''
                new_description = vals.get('job_description')

                if old_description.strip() != new_description.strip():
                    log_message = _(
                        "Job Description updated for **%s** on **%s**."
                        "<br/>**Previous Value:**<br/>%s"
                        "<br/>**New Value:**<br/>%s"
                    ) % (
                        employee.name,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        old_description,
                        new_description
                    )
                    
                    # This is the correct call on the recordset:
                    employee.message_post(
                        body=log_message,
                        subject=_("Job Description Update"), 
                    )

        res = super(HrEmployee, self).write(vals)
        return res

    @api.depends('doj', 'probation_term')
    def _compute_probation_end_date(self):
        for rec in self:
            rec.probation_end_date = False
            if not rec.doj or not rec.probation_term:
                continue

            term = rec.probation_term.strip().lower()
            match = re.match(r"(\d+)\s*(day|days|week|weeks|month|months)?", term)
            if match:
                value = int(match.group(1))
                unit = match.group(2)

                if not unit or 'day' in unit:
                    rec.probation_end_date = rec.doj + timedelta(days=value)
                elif 'week' in unit:
                    rec.probation_end_date = rec.doj + timedelta(weeks=value)
                elif 'month' in unit:
                    rec.probation_end_date = rec.doj + relativedelta(months=value)


    @api.model
    def update_iqama_number(self):
        # Retrieve all employees
        employees = self.env['hr.employee'].search([])

        # Loop through each employee
        for employee in employees:
            # Check if the employee has an employment visa
            visa = self.env['employment.visa'].search([('employee_id', '=', employee.id)], limit=1)

            # Check if the employee has a local transfer record
            local_transfer = self.env['local.transfer'].search([('employee_id', '=', employee.id)], limit=1)

            # Update iqama number based on the existence of employment visa or local transfer record
            if visa:
                employee.write({'iqama_no': visa.iqama_no})
            elif local_transfer:
                employee.write({'iqama_no': local_transfer.iqama_no})



    # @api.model
    # def create(self, vals):
    #     if vals.get('client_id'):
    #         sequence_code = 'seq_client_employee'
    #     else:
    #         sequence_code = 'seq_aamalcom_employee'

    #     vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.employee')
    #     if vals.get('user_id'):
    #         user = self.env['res.users'].browse(vals['user_id'])
    #         vals['custom_employee_type'] = user.user_type

    #     user = self.env.user
    #     if user.partner_id.is_client:
    #         vals['client_id'] = user.id


    #     employee = super(HrEmployee, self).create(vals)
    #     return employee

    @api.model
    def create(self, vals):
        if vals.get('custom_employee_type') == 'external':
            sequence_value = self.env['ir.sequence'].next_by_code('hr.employee.external')
        else:
            sequence_value = self.env['ir.sequence'].next_by_code('hr.employee.internal')


        if not sequence_value:
            raise ValueError("Sequence value could not be generated")

        vals['sequence'] = sequence_value

        if vals.get('user_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            vals['custom_employee_type'] = user.user_type

        user = self.env.user
        if user.partner_id.is_client:
            vals['client_id'] = user.id

        employee = super(HrEmployee, self).create(vals)

        return employee



    @api.depends('client_id')
    def update_project_manager(self):
        for line in self:
            line.company_spoc_id = line.client_id.company_spoc_id




class HrEmployeeCompany(models.Model):
    _name = 'hr.employee.company'
    _order = 'name desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Sister Companies"

    name = fields.Char(string="Name")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)