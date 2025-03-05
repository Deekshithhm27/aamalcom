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
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    first_approver_id = fields.Many2one('res.users', string="First Approver")
    final_approver_id = fields.Many2one('res.users', string="Final Approver")

    upload_payment_doc = fields.Binary(string="Payment Confirmation Document", tracking=True)

    def action_direct_post(self):
        self.action_post()

    def action_submit_for_approval(self):
        for line in self:
            if not line.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            line.state = 'approval_needed'


    def action_manager_approval(self):
        for line in self:
            line.state = 'approved'
            line.final_approver_id = self.env.user.id


    def action_first_approval(self):
        for line in self:
            line.state = 'manager_approval'
            line.first_approver_id = self.env.user.id