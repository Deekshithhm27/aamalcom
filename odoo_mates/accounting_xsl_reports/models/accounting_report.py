# models/accountong.py

# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountingReport(models.TransientModel):
    _name = "accounting.report"
    _description = "Accounting Report Wizard"

    account_report_id = fields.Many2one(
        'account.financial.report',
        string="Account Reports",
        required=True
    )
    target_move = fields.Selection([
        ('all', 'All Entries'),
        ('posted', 'All Posted Entries'),
    ], string='Target Moves', required=True, default='posted')

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    journal_ids = fields.Many2many('account.journal', string='Journals')
    enable_filter = fields.Boolean(string='Enable Comparison')
    filter_cmp = fields.Selection([('filter_no', 'No Filters')], string='Comparison')

    date_from_cmp = fields.Date(string='Start Date')
    date_to_cmp = fields.Date(string='End Date')
    label_filter = fields.Char(string='Filter Label', default='Comparison')
    debit_credit = fields.Boolean(
        string='Display Debit/Credit Columns',
        default=False,
        help="Shows debit and credit columns in the report if checked."
    )
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)

    def check_report(self):
        return self.print_report()

    def print_report(self):
        return self.env.ref(
            'accounting_pdf_reports.action_report_account_pdf'
        ).report_action(self)

    def print_xlsx_report(self):
        data = {
            'form': self.read([
                'date_from', 'date_to', 'journal_ids', 'target_move', 
                'debit_credit', 'enable_filter', 'filter_cmp', 'account_report_id',
                'company_id', 'date_from_cmp', 'date_to_cmp', 'label_filter'
            ])[0],
            'used_context': dict(self._context or {}, 
                                  lang=self.env.context.get('lang', 'en_US'), 
                                  tz=self.env.context.get('tz', 'UTC'), 
                                  uid=self.env.uid)
        }
        return self.env.ref(
            'accounting_xsl_reports.action_report_account_xlsx'
        ).report_action(self, data=data)