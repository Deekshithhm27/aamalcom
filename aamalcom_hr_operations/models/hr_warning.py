# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrWarningLetter(models.Model):
    _name = 'hr.warning'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Warning Letter'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        domain="[('custom_employee_type', '=', 'internal')]",
      
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    
    name = fields.Char(string='Request ID', 
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.warning'))
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    reason_for_warning = fields .Text(string="Reason")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_employee', 'Done'),
    ], string="Status", default="draft")

    # Correct One2many field pointing to the document model and the correct inverse field
    termination_document_ids = fields.One2many(
        'hr.resignation.document',
        'warning_id',
        string='Warning Documents'
    )
    #To auto populate details from MAster Record
    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
                
    def action_submit_to_employee(self):
        for record in self:
            record.state = 'submit_to_employee'
