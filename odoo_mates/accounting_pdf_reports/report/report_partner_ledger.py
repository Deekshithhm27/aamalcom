# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger'
    _description = 'Partner Ledger Report'

    def _lines(self, data, partner):
        """Fetch ledger lines for each partner, with residual filtering for receivable/payable only."""
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {})
        )._query_get()

        # Residual filter only on receivable/payable
        payment_type = data['form'].get('payment_type')
        residual_clause = ''
        if payment_type == 'paid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND ABS("account_move_line".amount_residual) < 0.01
            """
        elif payment_type == 'unpaid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND "account_move_line".amount_residual > 0.01
            """

        params = [
            tuple(data['computed']['account_ids']),
            tuple(data['computed']['move_state']),
            partner.id
        ] + query_get_data[2]

        query = f"""
            SELECT "account_move_line".id, "account_move_line".date, j.code,
                   acc.code as a_code, acc.name as a_name,
                   "account_move_line".ref, m.name as move_name,
                   "account_move_line".name, "account_move_line".debit,
                   "account_move_line".credit, "account_move_line".amount_currency,
                   "account_move_line".currency_id, c.symbol AS currency_code,
                   "account_move_line".amount_residual
            FROM {query_get_data[0]}
            JOIN account_move m ON (m.id="account_move_line".move_id)
            JOIN account_account account ON ("account_move_line".account_id = account.id)
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            WHERE "account_move_line".account_id IN %s
                AND m.state IN %s
                AND "account_move_line".partner_id = %s
                AND {query_get_data[1]} {residual_clause}
            ORDER BY "account_move_line".date
        """
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()

        # Running balance & formatting
        running_balance = 0.0
        for r in res:
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            running_balance += r['debit'] - r['credit']
            r['progress'] = running_balance
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        """Sum totals per partner (debit/credit/balance) with residual filter applied only to receivable/payable."""
        if field not in ['debit', 'credit', 'debit - credit']:
            return 0.0

        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {})
        )._query_get()

        # Residual filter for totals
        payment_type = data['form'].get('payment_type')
        residual_clause = ''
        if payment_type == 'paid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND ABS("account_move_line".amount_residual) < 0.01
            """
        elif payment_type == 'unpaid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND "account_move_line".amount_residual > 0.01
            """

        params = [
            tuple(data['computed']['account_ids']),
            tuple(data['computed']['move_state']),
            partner.id
        ] + query_get_data[2]

        query = f"""
            SELECT SUM({field})
            FROM {query_get_data[0]}
            JOIN account_move m ON (m.id = "account_move_line".move_id)
            JOIN account_account account ON ("account_move_line".account_id = account.id)
            WHERE "account_move_line".account_id IN %s
                AND m.state IN %s
                AND "account_move_line".partner_id = %s
                AND {query_get_data[1]} {residual_clause}
        """
        self.env.cr.execute(query, tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    @api.model
    def _get_report_values(self, docids, data=None):
        """Main entry point for Partner Ledger with residual-based Paid/Unpaid filtering."""
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {})
        )._query_get()

        # Move states
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']

        # Account types
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        # Get account IDs for those types
        self.env.cr.execute("""
            SELECT a.id FROM account_account a
            WHERE a.internal_type IN %s AND NOT a.deprecated
        """, (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]

        # Residual filter for partner list
        payment_type = data['form'].get('payment_type')
        residual_clause = ''
        if payment_type == 'paid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND ABS("account_move_line".amount_residual) < 0.01
            """
        elif payment_type == 'unpaid':
            residual_clause = """
                AND account.internal_type IN ('receivable', 'payable')
                AND "account_move_line".amount_residual > 0.01
            """

        params = [
            tuple(data['computed']['account_ids']),
            tuple(data['computed']['move_state'])
        ] + query_get_data[2]

        query = f"""
            SELECT DISTINCT "account_move_line".partner_id
            FROM {query_get_data[0]}
            JOIN account_account account ON ("account_move_line".account_id = account.id)
            JOIN account_move am ON (am.id = "account_move_line".move_id)
            WHERE "account_move_line".account_id IN %s
                AND am.state IN %s
                AND NOT account.deprecated
                AND {query_get_data[1]} {residual_clause}
        """
        self.env.cr.execute(query, tuple(params))

        partner_ids = data['form']['partner_ids'] or [
            res['partner_id'] for res in self.env.cr.dictfetchall()
        ]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        return {
            'doc_ids': partner_ids,
            'doc_model': 'res.partner',
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }
