# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ClientPayslipApproval(models.Model):
    _name = 'client.payslip.approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Payslip Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('client.payslip.approval')
    )

    from_date = fields.Date(string="From Date", required=True, tracking=True)
    to_date = fields.Date(string="To Date", required=True, tracking=True)

    approval_payslip_document = fields.Binary(string="Approval Payslip Document")
    approval_payslip_filename = fields.Char(string="Document Filename")
    updated_approval_payslip_document = fields.Binary(string="Updated Approval Payslip Document")
    reupdated_approval_payslip_document = fields.Binary(string="Re-Updtaed Approval Payslip Document")
    other_payslip_document = fields.Binary(string="Other Document")
    other_payslip_second_document = fields.Binary(string="Other Document")
    other_payslip__third_document = fields.Binary(string="Other Document")
    
    # New field to store the refusal reason
    refusal_reason = fields.Text(string="Refusal Reason", tracking=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_payroll', 'Submit to Payroll'),
        ('submit_to_pm', 'Submit to PM'),
        ('verified_by_pm', 'Verified By PM'),
        ('submit_to_payroll_employee', 'Submit to Payroll Employee'),
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

    def action_submit_to_payroll(self):
        for rec in self:
            rec.state = 'submit_to_payroll'
            rec.message_post(body="Payslip approval submitted to Payroll.")
        return True

    def action_submit_to_pm(self):
        for rec in self:
            rec.state = 'submit_to_pm'
            rec.message_post(body="Payslip updated and submitted to PM.")
        return True

    def action_reviewed_by_pm(self):
        for rec in self:
            rec.state = 'verified_by_pm'
            rec.message_post(body="Payslip verified by PM.")
        return True

    def action_submit_to_payroll_employee(self):
        for rec in self:
            rec.state = 'submit_to_payroll_employee'
            rec.message_post(body="Payslip submitted for Payroll Employee review.")
        return True

    def action_reviewed_by_payroll_employee(self):
        for rec in self:
            rec.state = 'submit_to_hr_manager'
            rec.message_post(body="Payslip submitted to HR Manager for final review.")
        return True

    def action_reviewed_by_hr_manager(self):
        for rec in self:
            rec.state = 'done'
            rec.message_post(body="Payslip process complete. The document is finalized.")
        return True

    # This method is now a button to open the wizard, not change the state directly
    def action_refused_by_pm(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'client.payslip.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payslip_approval_id': self.id,
            }
        }
    
class ClientPayslipRefuseWizard(models.TransientModel):
    _name = 'client.payslip.refuse.wizard'
    _description = 'Wizard to Refuse Payslip Approval'

    # The field to capture the reason from the user
    reason = fields.Text(string="Reason for Refusal", required=True)
    
    # This field links the wizard to the main record
    payslip_approval_id = fields.Many2one('client.payslip.approval', string="Payslip Approval")

    # The action that will be called by the "Refuse" button in the wizard
    def refuse_payslip(self):
        self.ensure_one()
        payslip = self.payslip_approval_id
        
        # Update the state of the main record
        payslip.state = 'refuse'
        
        # Store the reason on the main record
        payslip.refusal_reason = self.reason
        
        # Post the refusal reason to the chatter
        payslip.message_post(body="Payslip has been refused by PM with the following reason: <br/>%s" % self.reason)

        return {'type': 'ir.actions.act_window_close'}
