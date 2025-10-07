# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrResignation(models.Model):
    _name = 'hr.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Resignation'

    name = fields.Char(string='Request ID', store=True, 
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.resignation'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        store=True,
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
    resignation_date = fields.Date(
        string='Resignation Date',
        default=fields.Date.today(),
        store=True,
        readonly=True
    )
    last_working_day = fields.Date(
        string='Last Working Day',
        store=True,
        tracking=True
    )
    extend_last_working_day = fields.Date(
        string='Extended Working Day',
        tracking=True
    )
    reason = fields.Text(string='Reason for Resignation')
    manager_id = fields.Many2one(
        related='employee_id.parent_id',
        string="Project Manager",
        store=True
    )
    resignation_status = fields.Selection([
        ('accept_resignation','Accept Resignation'),
        ('postpone_resignation_request', 'Postpone Resignation'),
        ('rejected_resignation_request', 'Reject Resignation')
    ], string="Resignation Decision", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_hr', 'Submitted To HR'),
        ('submit_to_review', 'Submit To Review'),
        ('accepted_extension_date','Accepted'),
        ('acceptance_resignation', 'Resignation Accepted'),
        ('postpone_resignation', 'Resignation Postponed'),
        ('rejection', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ], string="Status", default="draft")
    
    is_hr_manager = fields.Boolean(
        string="Is HR Manager?",
        compute="_compute_is_hr_manager"
    )

    @api.depends()
    def _compute_is_hr_manager(self):
        for rec in self:
            rec.is_hr_manager = self.env.user.has_group('visa_process.group_service_request_hr_employee')

    termination_document_ids = fields.One2many(
        'hr.resignation.document', 
        'resignation_id', 
        string='Termination Documents'
    )

    

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
        return super(HrResignation, self).create(vals)

    def action_submit_to_hr(self):
        for record in self:
            if not record.last_working_day:
                raise ValidationError("Please specify Last Working Date")
            if not record.reason:
                raise ValidationError("Please specify Reason for Resignation")
            record.state = 'submit_to_hr'
            record.message_post(body=_("Resignation submitted to HR."))

    def action_withdraw(self):
        for record in self:
            record.state = 'withdrawn'
            record.message_post(body=_("Resignation request withdrawn."))

    def action_postpone_hr(self):
        for record in self:
            if not record.last_working_day:
                raise ValidationError("Please specify Extended Last Working Date")
            record.state = 'submit_to_review'
            record.message_post(body=_("Resignation request postponed and submitted for review."))

    def action_rejection_hr(self):
        for record in self:
            record.state = 'rejection'
            record.message_post(body=_("Resignation request rejected by HR."))

    def action_resignation_hr(self):
        for record in self:
            record.state = 'acceptance_resignation'
            record.message_post(body=_("Resignation request accepted by HR."))

    def action_accepted_employee(self):
        for record in self:
            record.state = 'accepted_extension_date'
            record.message_post(body=_("Extended last working date accepted by employee."))

    def action_postpone_accepted_date(self):
        for record in self:
            record.state = 'postpone_resignation'
            record.message_post(body=_("Resignation postponed with new accepted date."))
