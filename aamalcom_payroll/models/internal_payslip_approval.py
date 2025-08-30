# -*- coding: utf-8 -*-

from odoo import models, fields, api

class InternalPayslipApproval(models.Model):
    _name = 'internal.payslip.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Payslip Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('internal.payslip.approval')
    )

    from_date = fields.Date(string="From Date", required=True, tracking=True)
    to_date = fields.Date(string="To Date", required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_payroll', 'Submit to Payroll'),
        ('submit_to_pm', 'Submit to PM'),
        ('verified_by_pm', 'Verified By PM'),
        ('submit_to_hr_employee', 'Submit to HR Employee'),
        ('submit_to_hr_manager', 'Submit to HR Manager'),
        ('done', 'Done'),
        ('refuse', 'Refused by PM'),
    ], string="Status", default='draft', tracking=True)

    is_payroll_manager = fields.Boolean(
        string="Is Payroll Manager?",
        compute="_compute_is_payroll_manager"
    )

    @api.depends()
    def _compute_is_payroll_manager(self):
        """
        Check if the current user belongs to the payroll manager group.
        """
        for rec in self:
            rec.is_payroll_manager = self.env.user.has_group('visa_process.group_service_request_payroll_manager')


    employee_status = fields.Selection([('saudi_employee', 'Saudi Employee'),('non_saudi_employee', 'Non Saudi Employee')], string="Employee Status", store=True,required=True)

    def action_submit_to_payroll(self):
        for rec in self:
            rec.state = 'submit_to_payroll'
            rec.message_post(body="Payslip approval submitted to Payroll.")
        return True

    def action_submit_to_hr_employee(self):
        for rec in self:
            rec.state = 'submit_to_hr_employee'
            rec.message_post(body="Payslip submitted for Payroll Employee review.")
        return True

    def action_submit_to_hr_manager(self):
        for rec in self:
            rec.state = 'submit_to_hr_manager'
            rec.message_post(body="Payslip submitted for Payroll Employee review.")
        return True

    def action_reviewed_by_hr_manager(self):
        for rec in self:
            rec.state = 'done'
            rec.message_post(body="Payslip process complete. The document is finalized.")
        return True
