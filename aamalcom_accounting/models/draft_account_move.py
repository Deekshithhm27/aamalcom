# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class DraftAccountMove(models.Model):
    _name = 'draft.account.move'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    _order = 'date desc, name desc, id desc'
    _mail_post_access = 'read'
    _check_company_auto = True
    _description = 'Draft Invoice'



    name = fields.Char(string="Draft Invoice Number")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one(comodel_name='res.company', string='Company',
                                 store=True, readonly=True,
                                  default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")
    

    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    client_id = fields.Many2one('res.partner',string="Client Spoc")
    client_parent_id = fields.Many2one('res.partner',string="Client")
    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Ticket Ref")


    date = fields.Date(
        string='Created Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        tracking=True,
        default=fields.Date.context_today
    )

    invoiced_date = fields.Date(string="Invoiced Date")
    invoice_id = fields.Many2one('account.move',string="Invoice Ref")
    move_type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
            ('service_ticket','Service Ticket')
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="service_ticket", change_default=True)

    invoice_line_ids = fields.One2many('draft.account.move.line', 'move_id', string='Invoice lines',
        copy=False, readonly=True,
        states={'draft': [('readonly', False)]})

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('draft.account.move')
        res = super(DraftAccountMove,self).create(vals_list)
        return res

    untaxed_amount = fields.Monetary(string='Untaxed Amount', compute='_compute_totals', store=True)
    taxed_amount = fields.Monetary(string='Taxed Amount', compute='_compute_totals', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_totals', store=True)


    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.price_total', 'invoice_line_ids.tax_ids')
    def _compute_totals(self):
        for move in self:
            untaxed_total = 0.0
            tax_total = 0.0
            total = 0.0

            for line in move.invoice_line_ids:
                untaxed_total += line.price_subtotal
                tax_total += sum(line.tax_ids.mapped('amount'))
                total += line.price_total

            move.untaxed_amount = untaxed_total
            move.taxed_amount = tax_total
            move.total_amount = total

class DraftAccountMoveLine(models.Model):
    _name = 'draft.account.move.line'
    _description = 'Draft Account Move Line'

    move_id = fields.Many2one('draft.account.move', string='Journal Entry',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="The move of this entry line.")
    employee_id = fields.Many2one('hr.employee',string="Employee")
    name = fields.Char(string="Description")

    move_name = fields.Char(string='Number', related='move_id.name', store=True, index=True)
    date = fields.Date(related='move_id.date', store=True, readonly=True, index=True, copy=False, group_operator='min')
    parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")

    quantity = fields.Float(string='Quantity',
        default="1.0", digits='Product Unit of Measure',
        help="The optional quantity expressed by this line, eg: number of product sold. "
             "The quantity is not a legal requirement but is very useful for some reports.")
    price_unit = fields.Monetary(string='Unit Price', digits='Product Price')
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        context={'active_test': False},
        check_company=True,
        help="Taxes that apply on the base amount")

    price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True,
        currency_field='currency_id',compute="_compute_subtotal")
    price_total = fields.Monetary(string='Total', store=True, readonly=True,
        currency_field='currency_id',compute="_compute_total")

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_total(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            taxes = line.tax_ids.compute_all(subtotal)
            line.price_total = taxes['total_included']

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit