from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class AnnualRequestService(models.Model):
    _name = "hr.annual.request"
    _description = "Annual Request"
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
    annual_request_description = fields .Text(string="Details")
    department_id = fields.Many2one('hr.department', string="Department", compute="_compute_employee_details", store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved_by_dept_head', 'Waiting for HR Manager Approval'),
        ('submit_to_dept_head', 'Waiting for Approval By Department Head'),
        ('submit_to_gm','Waiting for GM Approval'),
        ('approved', 'Awaiting HR review'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
    ], string="Status", default="draft")
    
    confirmed_ticket_id = fields.Many2one(
        'hr.annual.request',
        string="Confirmed Ticket",
        domain=[('state', '=', 'approved')] # This domain filters tickets by their 'state'
    )
    
    is_my_coach = fields.Boolean(
        string="Is My Coach",
        compute='_compute_is_my_coach',
        store=False
    )
    is_hr_employee = fields.Boolean(
        string="Is HR Employee?",
        compute="_compute_is_hr_employee"
    )

    @api.depends()
    def _compute_is_hr_employee(self):
        """
        Check if the current user belongs to the HR manager group.
        """
        for rec in self:
            rec.is_hr_employee = self.env.user.has_group('visa_process.group_service_request_hr_employee')

    #This method used to check Dept head
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
                rec.department_id = rec.employee_id.department_id.id
            

    @api.model
    def create(self, vals):
        if not vals.get('employee_id'):
            employee = self.env.user.employee_id
            if employee:
                vals['employee_id'] = employee.id
        request = super(AnnualRequestService, self).create(vals)
        request.message_post(body="Annual Request created by %s" % request.employee_id.name)
        return request

    def action_submit_to_hr(self):
        for record in self:
            if not record.annual_request_description:
                raise ValidationError("Please add description")
            record.state = 'submit_to_dept_head'
            record.message_post(body="Request submitted for approval by Department Head")

    def action_approved_by_dept_head(self):
        for record in self:
            record.state = 'approved_by_dept_head'
            record.message_post(body="Approved by Department Head")
    
    def action_approved_by_hr(self):
        for record in self:
            record.state = 'submit_to_gm'
            record.message_post(body="Approved by HR")
    
    def action_approved_by_gm(self):
        for record in self:
            record.state = 'approved'
            record.message_post(body="Approved by General Manager")

    def process_complete(self):
        for record in self:
            record.state = 'done'
            record.message_post(body="Process completed")
