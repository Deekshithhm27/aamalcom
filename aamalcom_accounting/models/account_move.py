# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, float_is_zero, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.osv import expression

from datetime import date, timedelta,datetime
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings

import base64
from num2words import num2words



class AccountMove(models.Model):
    _inherit = 'account.move'
 
    
    draft_invoice_sequence = fields.Char('Draft Invoice Number', index=True, copy=False, default='New')

    invoice_type = fields.Selection([('direct','Direct Invoice'),('operation','Operations')],string="Invoice Type",default='direct',copy=False)

    invoice_initiated_by = fields.Many2one('res.users',string="Invoice initiated by")

    move_particulars_ids = fields.One2many('account.move.particulars','invoice_id',string="Particulars")
    amount_total_in_words = fields.Char(string="Total Amount In Words", compute="_compute_amount_total_in_words")
    # fields for alert : customer already has a same-amount invoice in the same month
    latest_existing_invoice_id = fields.Boolean(string='Has Duplicate Invoice', copy=False)
    latest_existing_invoice_name = fields.Char(string='Latest Duplicate Invoice', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('draft_invoice_sequence', 'New') == 'New':
            vals['draft_invoice_sequence'] = self.env['ir.sequence'].next_by_code('account.move.draft.invoice') or '/'
        return super(AccountMove, self).create(vals)


    @api.depends('amount_total', 'currency_id', 'partner_id.lang')
    def _compute_amount_total_in_words(self):
        for order in self:
            language = order.partner_id.lang or 'en'
            if order.currency_id:
                amount_in_words = num2words(order.amount_total, lang=language).title()
                order.amount_total_in_words = amount_in_words
            else:
                order.amount_total_in_words = "Currency not defined"

    # Warn when a customer already has a same-amount invoice in the same month
    @api.onchange('partner_id', 'invoice_line_ids', 'invoice_date')
    def _onchange_customer_amount_date(self):
        for record in self:
            record.latest_existing_invoice_id = False
            record.latest_existing_invoice_name = False
            # Checking account.move is invoice
            if self.move_type == 'out_invoice':
                # Get first and last date of the month
                month_start = record.date.replace(day=1)
                month_end = (month_start.replace(month=month_start.month % 12 + 1, day=1) - timedelta(days=1))

                # Search for duplicate records within the same month
                domain = [
                    ('partner_id', '=', record.partner_id.id),
                    ('amount_untaxed', '=', record.amount_untaxed),
                    ('invoice_date', '>=', month_start),
                    ('invoice_date', '<=', month_end),
                ]
                existing = self.env['account.move'].search(domain, limit=1)

                if existing:
                    record.latest_existing_invoice_id = True
                    record.latest_existing_invoice_name = existing.draft_invoice_sequence

    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    employee_id = fields.Many2one('hr.employee',string="Employee",store=True)
    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Enquiry Id")
    bank_ref = fields.Char(string="Bank Reference")

