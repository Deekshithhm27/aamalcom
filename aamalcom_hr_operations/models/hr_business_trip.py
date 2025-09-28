# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrBusinessTrip(models.Model):
    _name = 'hr.business.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Business Trip'

    name = fields.Char(string='Request ID', required=True, 
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.business.trip'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        readonly=True,
        tracking=True,
        default=lambda self: self.env.user.employee_id.id
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    iqama_no = fields.Char(string="Iqama No")
    identification_id = fields.Char(string='Border No.')
    passport_no = fields.Char(string='Passport No')
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    reason_of_business_trip = fields.Text(string="Specification of Business Trip")
    businees_trip_type = fields.Selection([
        ('inside_saudi_business_trip', 'Inside'),
        ('outside_saudi_business_trip', 'Outside')
    ], string="Business Trip Status", store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_hr', 'Submitted'),
        ('submit_to_fm', 'Approved by HR'),
        ('submit_to_gm','Approved by FM'),
        ('approve_businees_trip', 'Accepted'),
        ('refuse_business_trip', 'Refuse'),
    ], string="Status", default="draft")

    upload_business_trip_form = fields.Binary(string="Business Trip Form")
    
    is_hr_manager = fields.Boolean(
        string="Is HR Manager?",
        compute="_compute_is_hr_manager"
    )
    is_dept_head = fields.Boolean(
        string="Is Department Head",
        compute='_compute_is_dept_head',
        store=False
    )

    @api.depends()
    def _compute_is_dept_head(self):
        for rec in self:
            rec.is_dept_head = (
                self.env.user.has_group('visa_process.group_service_request_payroll_manager')
                or self.env.user.has_group('visa_process.group_service_request_insurance_manager')
                or self.env.user.has_group('visa_process.group_service_request_hr_manager')
                or self.env.user.has_group('visa_process.group_service_request_govt_manager')
            )

    @api.onchange('employee_id')
    def update_service_request_type_from_employee(self):
        for line in self:
            if line.employee_id:
                line.iqama_no = line.employee_id.iqama_no
                line.identification_id = line.employee_id.identification_id
                line.passport_no = line.employee_id.passport_id

    @api.depends()
    def _compute_is_hr_manager(self):
        for rec in self:
            rec.is_hr_manager = self.env.user.has_group('visa_process.group_service_request_hr_manager')

    @api.model
    def create(self, vals):
        if not vals.get('employee_id'):
            employee = self.env.user.employee_id
            if employee:
                vals['employee_id'] = employee.id
        return super(HrBusinessTrip, self).create(vals)

    def action_submit_to_hr(self):
        for record in self:
            record.state = 'submit_to_hr'
            record.message_post(body=_("Business trip submitted to HR."))

    def action_approved_by_hr(self):
        for record in self:
            record.state = 'submit_to_fm'
            record.message_post(body=_("Business trip approved by HR and sent to FM."))

    def action_approved_by_fm(self):
        for record in self:
            record.state = 'submit_to_gm'
            record.message_post(body=_("Business trip approved by FM and sent to GM."))

    def action_approved_by_gm(self):
        for record in self:
            record.state = 'approve_businees_trip'
            record.message_post(body=_("Business trip approved by GM. Trip accepted."))
