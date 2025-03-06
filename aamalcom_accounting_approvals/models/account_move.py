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

    def action_direct_post(self):
        self.action_post()

    def action_submit_for_approval(self):
        for line in self:
            if not line.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            line.state = 'approval_needed'


    def action_manager_approval(self):
        for line in self:
            if line.move_type != 'in_invoice':
                line.state = 'approved'
                line.final_approver_id = self.env.user.id
            if line.move_type == 'in_invoice':
                line.state = 'waiting_fin_approval'


    def action_first_approval(self):
        for line in self:
            line.state = 'manager_approval'
            line.first_approver_id = self.env.user.id

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


    def _compute_total_treasury_requests(self):
        for line in self:
            employee_id = self.env['service.request.treasury'].search([('account_move_id', '=', line.id)])
            line.total_treasury_requests = len(employee_id)