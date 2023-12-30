# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class VisaCandidate(models.Model):
    _name = 'visa.candidate'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Visa Candidate data"

    name = fields.Char(string="Name as per Passport",tracking=True,copy=False)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)
    sequence = fields.Char(string="Sequence",help="The Unique Sequence no", readonly=True, default='/')
    surname = fields.Char(string="Surname",tracking=True)
    given_name = fields.Char(string="Given Name",tracking=True)
    email = fields.Char(string="Email Id",tracking=True,required=True)
    dob = fields.Date(string="DOB",tracking=True,required=True)
    nationality_id = fields.Many2one('res.country',string="Nationality",tracking=True)
    
    
    contact_no = fields.Char(string="Contact # in the country")
    current_contact = fields.Char(string="Current Contact # (if Outside the country)")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
    religion = fields.Selection([('muslim','Muslim'),('non_muslim','Non-Muslim'),('others','Others')],string="Religion")
    work_location_id = fields.Many2one('hr.work.location',string="Work Location")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    client_id = fields.Many2one('res.partner',string="Client",default=lambda self: self.env.user.partner_id)

    iqama_certificate = fields.Binary(string="Iqama")
    degree_certificate = fields.Binary(string="Degree")


    
    doj = fields.Date(string="Projected Date of Joining",tracking=True)
    employment_duration = fields.Many2one('employment.duration',string="Duration of Employment",tracking=True)
    probation_term = fields.Char(string="Probation Term")
    notice_period = fields.Char(string="Notice Period")
    working_days = fields.Char(string="Working Days")
    weekly_off_days = fields.Char(string="Weekly Off (No. Of Days)")

    phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")
    current_phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")

    iqama = fields.Char(string="Designation on Iqama")


    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['sequence'] = self.env['ir.sequence'].next_by_code('visa.candidate')
        res = super(VisaCandidate,self).create(vals_list)
        return res


