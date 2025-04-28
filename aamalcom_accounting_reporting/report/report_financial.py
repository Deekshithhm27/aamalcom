# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportFinancial(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_financial'
    _description = 'Financial Reports'

    def get_account_lines(self, data):
        lines = super(ReportFinancial, self).get_account_lines(data)
        for line in lines:
            if line.get('type') == 'account':
                account_code = line.get('name').split(' ')[0]
                account = self.env['account.account'].search([('code', '=', account_code)], limit=1)
                if account:
                    account = self.env['account.account'].browse(account.id)
                    partners = []
                    if data['debit_credit']:
                        # Fetch partner data with debit and credit sums
                        partner_debit_credit_filter = self.env['account.move.line'].read_group(
                            [('account_id', '=', account.id)],
                            ['debit:sum', 'credit:sum', 'balance:sum'],  # Removed redundant fields
                            ['account_id', 'partner_id'],
                            lazy=False
                        )
                        for rec in partner_debit_credit_filter:
                            partner_group_vals = {
                                'partner': rec['partner_id'][1] if rec['partner_id'] else 'No Partner',
                                'debit': rec['debit'],
                                'credit': rec['credit'],
                                'balance': rec['balance'],
                            }
                            partners.append(partner_group_vals)
                        # Add the 'partners' key to the line dictionary
                        line['partners'] = partners
                    # Fetch comparison data if enabled
                    # elif data.get('enable_filter'):
                    #     print("\n============enter filter======")
                    #     comp_partner_lines = []
                    #     if data['enable_filter']:
                    #         comp_partner_lines = self.env['account.move.line'].with_context(
                    #             **data['comparison_context']).read_group(
                    #             [('account_id', '=', account.id)],
                    #             ['partner_id', 'balance_cmp',],
                    #             ['partner_id'],
                    #             lazy=False
                    #         )
                    #         print("\n====comp_partner_lines======", comp_partner_lines)
                    #         for rec in comp_partner_lines:
                    #             partner_group_vals = {
                    #                 'partner': rec['partner_id'][1] if rec['partner_id'] else 'No Partner',
                    #             }
                    #             partner_group_vals['balance_cmp'] = rec['balance'],
                    #             partners.append(partner_group_vals)
                    #         # Add the 'partners' key to the line dictionary
                    #         line['partners'] = partners
                            # comp_domain = [('account_id', '=', account.id)]
                            # if data.get('comparison_context'):
                            #     comp_domain += self.env['account.move.line']._query_get(data['comparison_context'])
                            # comp_partner_lines = self.env['account.move.line'].read_group(
                            #     comp_domain, ['partner_id', 'debit:sum', 'credit:sum'], ['partner_id'], lazy=False)
                        # comparison_partner_filter = self.env['account.move.line'].with_context(
                        #     data.get('comparison_context')
                        # ).read_group(
                        #     [('account_id', '=', account.id)],
                        #     ['balance', 'balance_cmp'],
                        #     ['account_id', 'partner_id'],
                        #     lazy=False)
                        # print("\n-------comparison_partner_filter------", comparison_partner_filter)
                        # for rec in comparison_partner_filter:
                        #     partner_group_vals = {
                        #         'partner': rec['partner_id'][1] if rec['partner_id'] else 'No Partner',
                        #         'balance': rec['balance'],
                        #         'balance_cmp': rec['balance']* float(rec.sign) or 0.0,
                        #     }
                        #     partners.append(partner_group_vals)

                    else:
                        # Fetch partner data for the account
                        partner_filter = self.env['account.move.line'].read_group(
                            [('account_id', '=', account.id)],
                            ['account_id', 'partner_id', 'balance'],
                            ['account_id', 'partner_id'],
                            lazy=False
                        )
                        for rec in partner_filter:
                            partner_group_vals = {
                                'partner': rec['partner_id'][1] if rec['partner_id'] else 'No Partner',
                                'balance': rec['balance'],
                            }
                            partners.append(partner_group_vals)
                        # Add the 'partners' key to the line dictionary
                        line['partners'] = partners

        return lines

