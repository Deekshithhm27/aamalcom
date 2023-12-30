# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    

    payment_approval_id = fields.Many2one('account.payment.approval',string="Payment source")