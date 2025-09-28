# report/report_xslxs.py

# -*- coding: utf-8 -*-
from odoo import models

class AccountReportXlsx(models.AbstractModel):
    # This name must match the XML reference in your ir.actions.report
    _name = 'report.accounting_xsl_reports.account_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Profit and Loss XLSX Report'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Profit and Loss')
        bold = workbook.add_format({'bold': True})

        # headers
        headers = ['Name', 'Debit', 'Credit', 'Balance']
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)

        row = 1
        # Correctly get the report lines from the 'data' dictionary
        report_lines = self.env['report.accounting_pdf_reports.report_financial'].get_account_lines(data['form'])

        for line in report_lines:
            # Write the data from the dictionary
            sheet.write(row, 0, line.get('name', ''))
            sheet.write(row, 1, line.get('debit', 0.0))
            sheet.write(row, 2, line.get('credit', 0.0))
            sheet.write(row, 3, line.get('balance', 0.0))
            row += 1