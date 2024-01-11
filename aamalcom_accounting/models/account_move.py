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

    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    employee_id = fields.Many2one('hr.employee',string="Employee")