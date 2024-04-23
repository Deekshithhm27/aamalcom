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


    state = fields.Selection(selection=[('draft', 'Draft'),
            ('approval_needed', 'Waiting for Approval'),
            ('manager_approval', 'Waiting for Manager Approval'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    invoice_type = fields.Selection([('direct','Direct Invoice'),('operation','Operations')],string="Invoice Type",default='direct',copy=False)

    invoice_initiated_by = fields.Many2one('res.users',string="Invoice initiated by")
    first_approver_id = fields.Many2one('res.users',string="First Approver")
    final_approver_id = fields.Many2one('res.users',string="Final Approver")

    move_particulars_ids = fields.One2many('account.move.particulars','invoice_id',string="Particulars")

    @api.model
    def create(self, vals):
        if vals.get('draft_invoice_sequence', 'New') == 'New':
            vals['draft_invoice_sequence'] = self.env['ir.sequence'].next_by_code('account.move.draft.invoice') or '/'
        return super(AccountMove, self).create(vals)

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

    def action_direct_post(self):
        self.action_post()


    # reports
    def action_invoice_tax_report(self, type):
        self.ensure_one()
        if type == 'tax_invoice':
            template = self.env.ref('aamalcom_accounting.email_template_edi_invoice_tax_etir', raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('account.account_invoice_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            active_ids=[self.id],
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_AA')])
        if language_id:
            language = language_id.iso_code
        amount_str = str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]
        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    employee_id = fields.Many2one('hr.employee',string="Employee")
    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Enquiry Id")

