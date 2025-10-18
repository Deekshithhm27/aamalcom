# from odoo import models, fields, api
# import io
# import base64
# import xlsxwriter

# class EmployeeExcelReportWizard(models.TransientModel):
#     _name = 'employee.excel.report.wizard'
#     _description = 'Employee Excel Report Wizard'

#     selection_type = fields.Selection(
#         [('all', 'All Employees'), ('particular', 'Particular Employee')],
#         string='Selection',
#         default='all',
#         required=True
#     )
#     employee_id = fields.Many2one('hr.employee', string="Employee")

#     def action_generate_excel(self):
#         # Prepare in-memory output
#         output = io.BytesIO()
#         workbook = xlsxwriter.Workbook(output, {'in_memory': True})
#         worksheet = workbook.add_worksheet("Employee Report")

#         # Add formatting
#         header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
#         cell_format = workbook.add_format({'border': 1})

#         # Headers
#         headers = ["Employee Name", "Employee ID", "Employee Iqama ID", "Bank Name", "Bank IBAN", "Sponsorship ID"]
#         for col, header in enumerate(headers):
#             worksheet.write(0, col, header, header_format)

#         # Get employees
#         if self.selection_type == 'all':
#             employees = self.env['hr.employee'].search([])
#         else:
#             employees = self.employee_id

#         # Data rows
#         row = 1
#         for emp in employees:
#             worksheet.write(row, 0, emp.name or '', cell_format)
#             worksheet.write(row, 1, emp.id or '', cell_format)
#             worksheet.write(row, 2, emp.iqama_no or '', cell_format)   # custom field
#             worksheet.write(row, 3, emp.bank_id.name or '', cell_format)
#             worksheet.write(row, 4, emp.bank_account_id.acc_number or '', cell_format)
#             worksheet.write(row, 5, emp.sponsor_id.sponsor_no or '', cell_format) # custom field
#             row += 1

#         workbook.close()

#         # Save file in Odoo
#         file_data = base64.b64encode(output.getvalue())
#         output.close()

#         attachment = self.env['ir.attachment'].create({
#             'name': 'Employee_Report.xlsx',
#             'type': 'binary',
#             'datas': file_data,
#             'res_model': 'employee.excel.report.wizard',
#             'res_id': self.id,
#             'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         })

#         return {
#             'type': 'ir.actions.act_url',
#             'url': '/web/content/%s?download=true' % attachment.id,
#             'target': 'self',
#         }

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import io
import base64

# If xlsxwriter isn't available, raise a clear error
try:
    import xlsxwriter
except Exception as e:
    xlsxwriter = None


class EmployeeExcelReportWizard(models.TransientModel):
    _name = 'employee.excel.report.wizard'
    _description = 'Employee Excel Report Wizard'

    selection_type = fields.Selection(
        [('all', 'All Employees'), ('particular', 'Particular Employee')],
        string='Selection',
        default='all',
        required=True
    )
    employee_id = fields.Many2one('hr.employee', string="Employee")

    def _get_employees(self):
        """Return recordset to export based on selection."""
        self.ensure_one()
        if self.selection_type == 'all':
            return self.env['hr.employee'].search([])
        return self.employee_id

    def action_generate_excel(self):
        self.ensure_one()
        if xlsxwriter is None:
            raise UserError(_("Python package 'xlsxwriter' is not installed."))

        # Prepare buffer
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_("Employee Report"))

        # Formats
        header = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align': 'center'})
        cell = workbook.add_format({'border': 1})
        text_wrap = workbook.add_format({'border': 1, 'text_wrap': True})

        # Column widths
        sheet.set_column(0, 0, 28)  # Employee Name
        sheet.set_column(1, 1, 14)  # Employee ID
        sheet.set_column(2, 2, 20)  # Iqama
        sheet.set_column(3, 3, 20)  # Bank Name
        sheet.set_column(4, 4, 30)  # IBAN
        sheet.set_column(5, 5, 18)  # Sponsorship ID

        # Headers
        headers = [
            _("Employee Name"),
            _("Employee ID"),
            _("Employee Iqama ID"),
            _("Bank Name"),
            _("Bank IBAN"),
            _("Sponsorship ID"),
        ]
        for col, h in enumerate(headers):
            sheet.write(0, col, h, header)

        # Data
        employees = self._get_employees()
        row = 1
        for emp in employees:
            # Safely pull values (avoid None in xlsx)
            emp_name = emp.name or ''
            emp_id = emp.id or ''
            iqama = getattr(emp, 'iqama_no', '') or ''
            bank_name = (getattr(emp, 'bank_id', False) and emp.bank_id.name) or ''
            iban = (getattr(emp, 'bank_account_id', False) and emp.bank_account_id.acc_number) or ''
            sponsor = (getattr(emp, 'sponsor_id', False) and emp.sponsor_id.sponsor_no) or ''

            sheet.write(row, 0, emp_name, cell)
            sheet.write(row, 1, emp_id, cell)
            sheet.write(row, 2, iqama, cell)
            sheet.write(row, 3, bank_name, cell)
            sheet.write(row, 4, iban, text_wrap)
            sheet.write(row, 5, sponsor, cell)
            row += 1

        workbook.close()
        file_data = base64.b64encode(output.getvalue())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'Employee_Report.xlsx',
            'type': 'binary',
            'datas': file_data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
