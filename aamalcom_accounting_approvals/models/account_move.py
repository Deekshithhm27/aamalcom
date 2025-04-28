# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models,_,api
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection=[('draft', 'Draft'),
            ('approval_needed', 'Waiting for Approval'),
            ('manager_approval', 'Waiting for Manager Approval'),
            ('approved', 'Approved'),
            ('waiting_fin_approval', 'Waiting FM Approval'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    first_approver_id = fields.Many2one('res.users', string="First Approver")
    final_approver_id = fields.Many2one('res.users', string="Final Approver")
    # Fields - Vendor Invoice Approval Flow
    fin_approver_id = fields.Many2one('hr.employee', string="Approved Finance Manager", copy=False)
    total_treasury_requests = fields.Integer(string="Request Details", compute="_compute_total_treasury_requests")
    upload_payment_doc = fields.Binary(string="Payment Confirmation Document", tracking=True)
    is_confirmation_doc_uploaded = fields.Boolean(string="Is Confirmation Document Uploaded", default=False)

    def _get_record_url(self):
        """Helper method to get the URL of the current record."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"

    @api.model
    def send_email_notification(self):
        # Define groups and record names based on move_type and state
        group_mapping = {
            ('in_invoice', 'approval_needed'): 'visa_process.group_service_request_operations_manager',
            ('in_invoice', 'manager_approval'): 'visa_process.group_service_request_general_manager',
            ('in_invoice', 'waiting_fin_approval'): 'visa_process.group_service_request_finance_manager',
            ('out_refund', 'approval_needed'): 'visa_process.group_service_request_operations_manager',
            ('out_refund', 'manager_approval'): 'visa_process.group_service_request_general_manager',
            ('out_refund', 'approved'): 'visa_process.group_service_request_finance_manager',
            ('out_refund', 'waiting_fin_approval'): 'visa_process.group_service_request_finance_manager',
            ('out_invoice', 'approval_needed'): 'visa_process.group_service_request_operations_manager',
            ('out_invoice', 'manager_approval'): 'visa_process.group_service_request_general_manager',
            ('out_invoice', 'approved'): 'visa_process.group_service_request_finance_manager',
        }
        record_type = (
            'Vendor Invoice' if self.move_type == 'in_invoice' else
            'Customer Invoice' if self.move_type == 'out_invoice' else
            'Credit Note'
        )
        record_name = f'{record_type} {self.draft_invoice_sequence}'

        # Get the appropriate group
        group_ref = group_mapping.get((self.move_type, self.state))

        group = self.env.ref(group_ref)
        users = group.mapped('users')

        # Determine email subject and body
        record_url = self._get_record_url()
        action_text = 'Review and Confirm' if self.state == 'approved' else 'Review and approval'

        # Send email to each user in the group
        for user in users:
            user_name = user.name
            body_html = f"""
                       <p>Dear {user_name},</p>
                       <p>A new {record_name} is for your {action_text}. Kindly take the necessary action at your earliest convenience.</p>
                       <p><a href='{record_url}'>View {record_name}</a></p>
                       <p>Thank you,</p>
                   """
            mail_values = {
                'subject': f'{action_text} - {record_name}',
                'email_to': user.partner_id.email,
                'body_html': body_html,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()

    def action_direct_post(self):
        self.action_post()

    def action_submit_for_approval(self):
        for line in self:
            if not line.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            line.state = 'approval_needed'
            # sent mail to Operational Manager for approving
            self.send_email_notification()

    def action_manager_approval(self):
        for line in self:
            if line.move_type != 'in_invoice':
                line.state = 'approved'
                line.final_approver_id = self.env.user.id
                # sent mail to Finance Manager for
                self.send_email_notification()
            if line.move_type == 'in_invoice':
                line.state = 'waiting_fin_approval'
                # sent mail to Finance Manager for approving
                self.send_email_notification()


    def action_first_approval(self):
        for line in self:
            line.state = 'manager_approval'
            line.first_approver_id = self.env.user.id
            # sent mail to General Manager for approving
            self.send_email_notification()

    def action_finance_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for line in self:
            if line.move_type == 'in_invoice':
                vals = {
                'account_move_id': self.id,
                'client_id': self.partner_id.id,
                'client_parent_id':self.partner_id.parent_id.id,
                'employee_id':self.invoice_line_ids.employee_id.id,
                'total_amount':self.amount_total
                }
                service_request_treasury_id = self.env['service.request.treasury'].sudo().create(vals)

                if service_request_treasury_id:
                    service_request_treasury_id.state = 'submitted'
                    line.state = 'approved'
                    line.fin_approver_id = current_employee

            # Credit note create be any team member from finance, then First approval will be by Finance manager,
            if line.move_type == 'out_refund':
                line.state = 'waiting_fin_approval'
                self.send_email_notification()

    def _compute_total_treasury_requests(self):
        for line in self:
            employee_id = self.env['service.request.treasury'].search([('account_move_id', '=', line.id)])
            line.total_treasury_requests = len(employee_id)