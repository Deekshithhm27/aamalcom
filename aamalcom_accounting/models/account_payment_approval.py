# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountPaymentApproval(models.Model):
    _name = 'account.payment.approval'
    _order = 'name asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Payment Approval"

    name = fields.Char(string="Sequence",default="/")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")

    amount = fields.Monetary(string="Total Amount",currency_field='currency_id',readonly=True)

    client_id = fields.Many2one('res.partner',string="Client",readonly=True)
    client_parent_id = fields.Many2one('res.partner',string="Client",readonly=True)
    employee_id = fields.Many2one('hr.employee',domain="[('custom_employee_type', '=', 'external')]",string="Employee",readonly=True)

    state = fields.Selection([('draft','Draft'),('waiting','Waiting for Approval'),('approved','Approved'),
        ('cancel','Cancel'),('reject','Reject')],default="draft",string="Status",tracking=True)

    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Ticket",readonly=True)
    created_on = fields.Date(string="Created on",readonly=True,copy=False,
        default=fields.Date.context_today,tracking=True)

    manager_user_id = fields.Many2one('res.users',default=lambda self: self.env.user.employee_id.parent_id.user_id,readonly=True,copy=False)

    notes = fields.Text(string="Note")


    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.approval')
        res = super(AccountPaymentApproval,self).create(vals_list)
        return res

    def action_submit(self):
        for line in self:
            line.state = 'waiting'
            self._add_followers()

    def action_approve(self):
        for line in self:
            vals = {
                'partner_id': self.client_id.id,
                'amount':self.amount,
                'payment_approval_id':self.id,
                'payment_type': 'inbound',
                'ref': 'Payment request against %s Ticket' % (self.service_enquiry_id.name)
            }
            payment_id = self.env['account.payment'].sudo().create(vals)
            if payment_id:
                line.state = 'approved'

    def action_cancel(self):
        for line in self:
            line.state = 'cancel'

    def action_reject(self):
        for line in self:
            line.state = 'reject'
    #         

    def _add_followers(self):
        partner_ids = []
        partner_ids.append(self.env['res.users'].sudo().browse(self.env.uid).employee_id.parent_id.user_id.partner_id.id)

        self.message_subscribe(partner_ids=partner_ids)