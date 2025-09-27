# models/account_report_general_ledger.py

# -*- coding: utf-8 -*-
from odoo import models, fields, api
import time

class AccountGeneralLedgerReport(models.TransientModel):
    _name = "account.report.general.ledger"
    _description = "General Ledger Report Wizard"

    target_move = fields.Selection([
        ('all', 'All Entries'),
        ('posted', 'All Posted Entries')
    ], string='Target Moves', required=True, default='posted')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'), ('not_zero', 'With balance not equal to zero')], string='Display Accounts', required=True, default='movement')
    initial_balance = fields.Boolean(string='Include Initial Balance', default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    journal_ids = fields.Many2many('account.journal', string='Journals')
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')
    account_ids = fields.Many2many('account.account', string='Accounts')
    partner_ids = fields.Many2many('res.partner', string='Partners')
    
    def check_report(self):
        pass
    
    def print_xlsx_report(self):
        """
        Prepares the data and calls the XLSX report action.
        """
        # Read all necessary fields from the wizard, including the missing 'company_id'
        wizard_data = self.read([
            'date_from', 'date_to', 'journal_ids', 'target_move',
            'analytic_account_ids', 'account_ids', 'partner_ids',
            'sortby', 'display_account', 'initial_balance', 'company_id', # ✅ ADDED 'company_id'
        ])[0]

        # Create the data dictionary with the 'form' key
        data = {
            'form': wizard_data,
            'used_context': dict(self._context or {},
                                 lang=self.env.context.get('lang', 'en_US'),
                                 tz=self.env.context.get('tz', 'UTC'),
                                 uid=self.env.uid)
        }

        # Call the report action, passing the prepared data
        return self.env.ref(
            'accounting_xsl_reports.action_report_general_ledger_xlsx'
        ).report_action(self, data=data)