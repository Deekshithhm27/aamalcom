# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class InvoiceParticulars(models.Model):
    _name = 'account.move.particulars'
    _rec_name = "invoice_id"

    invoice_id = fields.Many2one('account.move')

    employee_id = fields.Many2one('hr.employee',string="Employee")

    particulars_line_ids = fields.One2many('account.move.line.particulars','particulars_id',string="Particular Lines")
    company_id = fields.Many2one(related='invoice_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")

class InvoiceParticularsLine(models.Model):
    _name = 'account.move.line.particulars'

    particulars_id = fields.Many2one('account.move.particulars',string="Particulars Ref")
    name = fields.Char(string="Description")
    company_id = fields.Many2one(related='particulars_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")
    amount = fields.Monetary(string="Amount")