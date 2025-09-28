# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PartnerLedgerXlsx(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Partner Ledger XLSX Report'

    def generate_xlsx_report(self, workbook, data, partners):
        # We'll use the original report's _get_report_values method to get all the data
        report_obj = self.env['report.accounting_pdf_reports.report_partnerledger']
        report_data = report_obj._get_report_values(partners.ids, data)

        # Define styles
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'center', 'border': 1})
        bold_format = workbook.add_format({'bold': True})
        text_format = workbook.add_format({'align': 'left'})
        money_format = workbook.add_format({'num_format': '#,##0.00'})
        
        sheet = workbook.add_worksheet('Partner Ledger')
        
        # Set column widths
        sheet.set_column('A:A', 12)  # Date
        sheet.set_column('B:B', 6)   # JRNL
        sheet.set_column('C:C', 10)  # Account
        sheet.set_column('D:D', 40)  # Ref
        sheet.set_column('E:G', 15)  # Debit, Credit, Balance
        sheet.set_column('H:H', 15)  # Currency

        # Write the main headers
        sheet.write('A1', 'Date', header_format)
        sheet.write('B1', 'JRNL', header_format)
        sheet.write('C1', 'Account', header_format)
        sheet.write('D1', 'Ref', header_format)
        sheet.write('E1', 'Debit', header_format)
        sheet.write('F1', 'Credit', header_format)
        sheet.write('G1', 'Balance', header_format)

        if data['form']['amount_currency']:
            sheet.write('H1', 'Currency', header_format)
            
        row = 1
        for partner in report_data['docs']:
            # Partner summary row
            sheet.write(row, 0, partner.ref or '', bold_format)
            sheet.write(row, 1, partner.name, bold_format)
            sheet.write(row, 4, report_data['sum_partner'](data, partner, 'debit'), money_format)
            sheet.write(row, 5, report_data['sum_partner'](data, partner, 'credit'), money_format)
            sheet.write(row, 6, report_data['sum_partner'](data, partner, 'debit - credit'), money_format)
            row += 1
            
            # Detailed lines for the partner
            for line in report_data['lines'](data, partner):
                sheet.write(row, 0, line['date'], text_format)
                sheet.write(row, 1, line['code'], text_format)
                sheet.write(row, 2, line['a_code'], text_format)
                sheet.write(row, 3, line['displayed_name'], text_format)
                sheet.write(row, 4, line['debit'], money_format)
                sheet.write(row, 5, line['credit'], money_format)
                sheet.write(row, 6, line['progress'], money_format)
                if data['form']['amount_currency']:
                    if line['amount_currency']:
                        currency_id = self.env['res.currency'].browse(line['currency_id'].id)
                        currency_format = workbook.add_format({'num_format': currency_id.symbol + ' #,##0.00'})
                        sheet.write(row, 7, line['amount_currency'], currency_format)
                    else:
                        sheet.write(row, 7, '', text_format)
                row += 1