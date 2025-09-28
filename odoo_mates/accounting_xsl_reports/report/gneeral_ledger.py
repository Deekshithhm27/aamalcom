# report/general_ledger_xlsx.py

# -*- coding: utf-8 -*-
from odoo import models

class GeneralLedgerXlsx(models.AbstractModel):
    _name = 'report.accounting_xsl_reports.general_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'General Ledger XLSX Report'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('General Ledger')
        bold = workbook.add_format({'bold': True})

        # Get the report data from the original General Ledger report model
        report_data = self.env['report.accounting_pdf_reports.report_general_ledger'].with_context(data.get('used_context', {}))._get_report_values(
            docids=None, data=data
        )
        accounts_res = report_data.get('Accounts')
        
        # --- Write Headers ---
        headers = ['Date', 'JRNL', 'Partner', 'Ref', 'Move', 'Analytic Account', 'Entry Label', 'Debit', 'Credit', 'Balance', 'Currency']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        row = 1
        # --- Write Report Data ---
        for account in accounts_res:
            # Write account header row
            sheet.write(row, 0, account['code'] + ' - ' + account['name'], bold)
            sheet.write(row, 7, account['debit'], bold)
            sheet.write(row, 8, account['credit'], bold)
            sheet.write(row, 9, account['balance'], bold)
            row += 1

            # Write move lines for the account
            for line in account['move_lines']:
                sheet.write(row, 0, line['ldate'] or '')
                sheet.write(row, 1, line['lcode'] or '')
                sheet.write(row, 2, line['partner_name'] or '')
                sheet.write(row, 3, line['lref'] or '')
                sheet.write(row, 4, line['move_name'] or '')
                sheet.write(row, 5, line['analytic_account_id'] or '')
                sheet.write(row, 6, line['lname'] or '')
                sheet.write(row, 7, line['debit'])
                sheet.write(row, 8, line['credit'])
                sheet.write(row, 9, line['balance'])
                sheet.write(row, 10, line['currency_code'] or '')
                row += 1