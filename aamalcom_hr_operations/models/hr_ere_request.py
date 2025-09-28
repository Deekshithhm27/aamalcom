# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ExitReentryService(models.Model):
    _name = "hr.exit.reentry"
    _description = "ExitReentryService"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request ID',
                       default=lambda self: self.env['ir.sequence'].next_by_code('hr.annual.request'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        readonly=True,
        tracking=True,
        default=lambda self: self.env.user.employee_id.id
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('submit_to_dept_head', 'Waiting for Approval By Department Head'),
        ('approved_by_dept_head', 'Waiting for HR Manager Approval'),
        ('submit_to_fm', 'Waiting for FM Approval'),
        ('submit_to_gm', 'Waiting for GM Approval'),
        ('submit_to_treasury', 'Waiting for Treasury Approval'),
        ('approved', 'Approved'),
        ('submitted_to_gre', 'Awaiting Documents Upload'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
    ], string="Status", default="draft")
    is_gov_employee = fields.Boolean(compute='_compute_is_gov_employee', store=False)

    is_my_coach = fields.Boolean(
        string="Is My Coach",
        compute='_compute_is_my_coach',
        store=False
    )
    is_hr_employee = fields.Boolean(
        string="Is HR Employee?",
        compute="_compute_is_hr_employee"
    )
    exit_date = fields.Date(
        string='Exit Date',
        store=True,
        tracking=True
    )

    @api.model
    def default_get(self,fields):
        res = super(ExitReentryService,self).default_get(fields)
        service_request_config_id = self.env['service.request.config'].search([('service_request_type','=','ev_request'),('service_request','=','exit_reentry_issuance')])
        print('service_request_config_id ',service_request_config_id)
        res.update({
            'service_request_config_id':service_request_config_id.id
            })
        return res

    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request','=','exit_reentry_issuance'),('service_request_type','=','ev_request')]",copy=False)
    
    employment_duration = fields.Many2one('employment.duration',string="Duration",tracking=True,domain="[('service_request_type','=','ev_request'),('service_request_config_id','=',service_request_config_id)]")


    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,)
    
    self_bill_string = fields.Char(string="Self Bill String", compute="_compute_self_bill_string")
    self_pay = fields.Boolean(string="Self")
    aamalcom_pay_string = fields.Char(string="Aamalcom Pay String", compute="_compute_self_bill_string")
    aamalcom_pay = fields.Boolean(string="Aamalcom")
    employee_pay_string = fields.Char(string="Employee Pay String")
    employee_pay = fields.Boolean(string="Self")
    self_bill = fields.Boolean(string="Self")
    billable_to_aamalcom_string = fields.Char(string="Billable to Aamalcom", compute="_compute_self_bill_string")
    billable_to_aamalcom = fields.Boolean(string="Billable to Aamalcom")
    confirmation_doc = fields.Binary(string="Confirmation Doc*")
    confirmation_doc_filename= fields.Binary(string="Conformation Document")
    confirmation_doc_ref = fields.Char(string="Ref No.*")
    payment_doc = fields .Binary(string="Payment Confirmation Document")
    treasury_confirmation_doc = fields.Binary(
        string="Payment Confirmation Doc",
        copy=False,
        attachment=True,
    )
    treasury_confirmation_ref = fields.Char(
        string="Ref No.",
        copy=False,
    )
    
    is_gov_employee = fields.Boolean(compute='_compute_is_gov_employee', store=False)
    @api.depends('is_gov_employee')
    def _compute_is_gov_employee(self):
        for record in self:
            # Check if the user is in gov employee groups
            record.is_gov_employee = self.env.user.has_group('visa_process.group_service_request_employee')


    muqeem_points = fields.Integer(string="Points")
    final_muqeem_cost = fields.Monetary(
        string="Final Muqeem Points Cost (with VAT)",
        currency_field='currency_id',
        compute='_compute_final_muqeem_cost',
    )
    total_treasury_requests = fields.Integer(
        string="Treasury Requests",
        compute="_compute_total_treasury_requests"
    )

    
    
    def _compute_total_treasury_requests(self):
        for rec in self:
            rec.total_treasury_requests = self.env['hr.service.request.treasury'].search_count(
                [('service_request_ref', '=', f'hr.exit.reentry,{rec.id}')]
            )
    
    
    # New field to link to the created treasury document
    treasury_request_id = fields.Many2one(
        'hr.service.request.treasury', 
        string="Treasury Request", 
        readonly=True,
        copy=False,
    )
    # @api.depends('is_gov_employee')
    def _compute_is_gov_employee(self):
        for record in self:
            # Check if the user is in gov employee groups
            record.is_gov_employee = self.env.user.has_group('visa_process.group_service_request_employee')



    @api.onchange('final_muqeem_cost')
    def _update_muqeem_pricing_line(self):
        for line in self:
            if line.final_muqeem_cost:
                line.service_enquiry_pricing_ids += self.env['service.enquiry.pricing.line'].create({
                        'name': 'Muqeem Fee',
                        'amount':line.final_muqeem_cost,
                        'service_enquiry_id': line.id
                        })
                
    @api.depends('muqeem_points')
    def _compute_final_muqeem_cost(self):
        for record in self:
            if record.muqeem_points:
                base_cost = record.muqeem_points * 0.2
                vat_cost = base_cost * 0.15
                total = base_cost + vat_cost
                record.final_muqeem_cost = round(total, 2)
            else:
                record.final_muqeem_cost = 0.0

    
    
    @api.depends()
    def _compute_is_hr_employee(self):
        for rec in self:
            rec.is_hr_employee = self.env.user.has_group('visa_process.group_service_request_hr_employee')

    @api.depends('employee_id')
    def _compute_is_my_coach(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.coach_id:
                current_user_employee = self.env.user.employee_id
                rec.is_my_coach = (current_user_employee == rec.employee_id.coach_id)
            else:
                rec.is_my_coach = False

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
    
    @api.model
    def create(self, vals):
        if not vals.get('employee_id'):
            employee = self.env.user.employee_id
            if employee:
                vals['employee_id'] = employee.id
        return super(ExitReentryService, self).create(vals)

    # Fields - Exit Rentry issuance
    exit_type = fields.Selection([('single', 'Single'), ('multiple', 'Multiple')], string="Type", store=True)
    to_be_issued_date = fields.Date(string="To be issued from")
    upload_confirmation_of_exit_reentry = fields.Binary(string="Upload Confirmation of Exit re-entry", store=True)
    upload_confirmation_of_exit_reentry_file_name = fields.Char(string="Upload Confirmation of Exit re-entry")
    confirmation_of_exit_reentry_ref = fields.Char(string="Ref No.*")
    upload_exit_reentry_visa = fields.Binary(string="Exit Re-entry Visa")
    upload_exit_reentry_visa_file_name = fields.Char(string="Exit Re-entry Visa File Name")
    exit_reentry_visa_ref = fields.Char(string="Ref No.*")

    
    ##Below Methods are used if aamalcom is choosen
    def action_submit_ere(self):
        for record in self:
            record.state = 'submit_to_dept_head'
            record.message_post(body=_("Request has been submitted to Department Head for approval."))

    def action_approval_dept(self):
        for record in self:
            record.state = 'approved_by_dept_head'
            record.message_post(body=_("Request has been approved by the Department Head and sent to the HR Manager for approval."))

    def action_approval_hr(self):
        for record in self:
            record.state = 'submit_to_gm'
            record.message_post(body=_("Request has been approved by the HR Manager and sent to the General Manager for approval."))

    def action_approval_gm(self):
        for record in self:
            record.state = 'submit_to_fm'
            record.message_post(body=_("Request has been approved by the General Manager and sent to the Finance Manager for approval."))

    def action_approval_fm(self):
        self.ensure_one()
        
        # 1. Create the treasury document
        treasury_vals = {
            'service_request_ref': 'hr.exit.reentry,%s' % self.id,
            'service_type': 'exit_reentry',
            'employee_id': self.employee_id.id,
            'total_amount': self.final_muqeem_cost,
            'exit_type': self.exit_type,
            'state': 'submitted',
        }
        
        treasury_request = self.env['hr.service.request.treasury'].create(treasury_vals)
        
        # 2. Update the state of the current record and link to the new treasury document
        self.write({
            'state': 'submit_to_treasury',
            'treasury_request_id': treasury_request.id,
        })
        
        # 3. Add a log note for the state change
        self.message_post(body=_("Request has been approved by the Finance Manager. A treasury request has been created."))

        # 4. Optional: Return an action to open the newly created treasury document
        return {
            'type': 'ir.actions.act_window',
            'name': 'Treasury Request',
            'res_model': 'hr.service.request.treasury',
            'res_id': treasury_request.id,
            'view_mode': 'form',
            'target': 'current',
        }
    def action_view_treasury_requests(self):
        self.ensure_one()
        return {
            'name': _('Treasury Requests'),
            'view_mode': 'tree,form',
            'res_model': 'hr.service.request.treasury',
            'type': 'ir.actions.act_window',
            'domain': [('service_request_ref', '=', f'hr.exit.reentry,{self.id}')],
            'context': {'create': False}
        }
    ##Methods end for Aamalcom process

    ##methods if Employee is chosen

    def action_submit_if_employee(self):
        for record in self:
            record.state = 'submit'
            record.message_post(body=_("Request has been submitted by the employee."))


    def action_done_ere(self):
        for record in self:
            if record.upload_confirmation_of_exit_reentry and not record.confirmation_of_exit_reentry_ref:
                raise ValidationError(
                    "Kindly Update Reference Number for Upload Confirmation of Exit re-entry Document")
            if record.upload_exit_reentry_visa and not record.exit_reentry_visa_ref:
                raise ValidationError("Kindly Update Reference Number for Exit Re-entry Visa Document")
            record.state = 'done'
            record.message_post(body=_("Exit/Re-entry Visa processing is now complete."))



class ServiceEnquiryPricingLine(models.Model):
    _inherit = 'service.enquiry.pricing.line'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
                                  related="company_id.currency_id", help="The payment's currency.")
