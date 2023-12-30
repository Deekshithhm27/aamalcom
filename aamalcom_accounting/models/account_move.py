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
 
    
    draft_invoice_sequence = fields.Char('Draft Invoice Number', copy=False, index=True)


    state = fields.Selection(selection=[('draft', 'Draft'),
            ('approval_needed', 'Waiting for Approval'),
            ('manager_approval', 'Waiting for Manager Approval'),
            ('approved', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    # @api.model
    # def create(self, vals):
    #     if vals.get('state') == 'draft':
    #         sequence_id = self.env['draft.invoice.sequence'].search([], limit=1)
    #         if sequence_id:
    #             vals['draft_invoice_sequence_id'] = sequence_id.id
    #             vals['name'] = 'DI/' + sequence_id.sequence.zfill(5)
    #             sequence_id.sequence = str(int(sequence_id.sequence) + 1).zfill(5)
    #     return super(AccountMove, self).create(vals)
    @api.model
    def create(self, vals):
        print("---------bbbbbbb",vals.get('move_type'))
        print("---------kjjjjjjjjjjjjjbbbbbbb",vals.get('state'))
        # if vals.get('move_type') == 'out_invoice':
        draft_invoice_sequence = self.env['ir.sequence'].next_by_code('account.move.draft.invoice')
        vals['draft_invoice_sequence'] = draft_invoice_sequence
        return super(AccountMove, self).create(vals)



    # def unlink(self):
    #     for invoice in self:
    #         if invoice.state == 'draft' and invoice.draft_invoice_sequence_id:
    #             invoice.draft_invoice_sequence_id.sequence = str(int(invoice.draft_invoice_sequence_id.sequence) - 1).zfill(5)
    #     return super(AccountMove, self).unlink()

    def action_submit_for_approval(self):
        for line in self:
            if not line.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            line.state = 'approval_needed'

    def action_manager_approval(self):
        for line in self:
            line.state = 'approved'

    
    def action_first_approval(self):
        for line in self:
            line.state = 'manager_approval'

    

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    employee_id = fields.Many2one('hr.employee',string="Employee")