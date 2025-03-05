# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_approval_id = fields.Many2one('account.payment.approval', string="Payment source")