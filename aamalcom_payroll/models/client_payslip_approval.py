# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
import io
import base64

# Import openpyxl for Excel generation
try:
    import openpyxl
except ImportError:
    openpyxl = None
    import logging
    _logger = logging.getLogger(__name__)
    _logger.warning("The openpyxl module is not installed. Payroll Excel generation will not work.")


class ClientPayslipApproval(models.Model):
    _name = 'client.payslip.approval'
    _description = "Client Payroll Approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Payslip Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('client.payslip.approval')
    )
    client_parent_id = fields.Many2one('res.partner',string="Client",required=True,domain=[('is_company','=',True)])
    client_id = fields.Many2one('res.users',string="Client SPOC",related="client_parent_id.client_id", store=True)

    from_date = fields.Date(string="From Date", required=True, tracking=True)
    to_date = fields.Date(string="To Date", required=True, tracking=True)
    create_date = fields.Datetime(string="Create Date", readonly=True, default=lambda self: datetime.now())
    processed_date = fields.Datetime(string="Processed Date", readonly=True, tracking=True)
    
    approval_payslip_document = fields.Binary(string="Approval Payroll Document")
    approval_payslip_filename = fields.Char(string="Document Filename")
    
    # NEW FIELDS FOR THE GENERATED DOCUMENT (UPDATED)
    generated_payroll_document = fields.Binary(string="Generated Payroll Document")
    generated_payroll_filename = fields.Char(string="Generated Filename")
    
    payslip_documents_ids = fields.One2many(
        comodel_name='client.payslip.document',
        inverse_name='payslip_approval_id',
        string='Updated Documents'
    )
    refusal_reason = fields.Text(string="Refusal Reason", tracking=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_payroll', 'Submitted for Verification'),
        ('submit_to_payroll_employee', 'Submitted to Payroll Employee'),
        ('submit_to_payroll_manager', 'Submitted to Payroll Manager'),
        ('done', 'Approved Authorized Confirmed'),
    ], string="Status", default='draft', tracking=True)

    is_payroll_manager = fields.Boolean(
        string="Is Payroll Manager?",
        compute="_compute_is_payroll_manager"
    )
    
    approval_document_date = fields.Date(string="Approval Document Date", compute="_compute_approval_document_date", store=True)

    @api.depends('approval_payslip_document')
    def _compute_approval_document_date(self):
        """
        Set the date when the approval document is uploaded.
        """
        for rec in self:
            # You might want to change this to look at generated_payroll_document
            if rec.approval_payslip_document and not rec.approval_document_date:
                rec.approval_document_date = date.today()
            elif not rec.approval_payslip_document:
                rec.approval_document_date = False
    def _get_related_salary_records(self):
        """Helper function to find the relevant salary tracking records."""
        return self.env['client.emp.salary.tracking'].search([
            ('client_parent_id', '=', self.client_parent_id.id),
            ('date_start', '>=', self.from_date),
            ('date_end', '<=', self.to_date),
            # Do not filter by state here, as we need all records for the period once the process starts
            ])
    
    @api.depends()
    def _compute_is_payroll_manager(self):
        """
        Check if the current user belongs to the payroll manager group.
        """
        for rec in self:
            # Assuming 'visa_process.group_service_request_payroll_manager' is the group's external ID
            rec.is_payroll_manager = self.env.user.has_group('visa_process.group_service_request_payroll_employee')
    
    def action_generate_payroll_xsl(self):
            self.ensure_one()

            if not openpyxl:
                raise UserError(_("The 'openpyxl' Python library is required to generate the Excel file. Please install it."))

            # 1. Search for records in client.emp.salary.tracking
            domain = [
                ('client_parent_id', '=', self.client_parent_id.id),
                ('date_start', '>=', self.from_date),
                ('date_end', '<=', self.to_date),
                ('state', '=', 'draft'), # Only include records in Draft state
            ]

            salary_records = self.env['client.emp.salary.tracking'].search(domain)

            if not salary_records:
                raise UserError(_("No employee salary tracking records in 'Draft' found for the selected client and period."))

            # 2. Generate an XSL (Excel) file
            output = io.BytesIO()
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Client Payroll"

            # Define headers (data population logic removed for brevity, assuming it's correct)
            # ... (Excel generation logic) ...
            headers = [
                "Sequence", "Employee", "Employee ID", "Client", "Date From", "Date To",
                "Worked Days", "Basic Salary", "HRA", "Travel Allowance",
                "Other Allowance", "Other Deductions", "Arrears", "Advances",
                "Overtime", "Additions", "Gross Salary", "Gosi Charges"
            ]
            sheet.append(headers)

            # Populate data rows
            for record in salary_records:
                row = [
                    record.name,
                    record.employee_id.name or '',
                    record.client_emp_sequence or '',
                    record.client_parent_id.name or '',
                    record.date_start.strftime('%Y-%m-%d') if record.date_start else '',
                    record.date_end.strftime('%Y-%m-%d') if record.date_end else '',
                    record.worked_days,
                    record.wage,
                    record.hra,
                    record.travel_allowance,
                    record.other_allowance,
                    record.other_deductions,
                    record.arrears,
                    record.advances,
                    record.overtime,
                    record.additions,
                    record.gross_salary,
                    record.gosi_charges,
                ]
                sheet.append(row)
                
            workbook.save(output)
            output.seek(0)
            excel_data = output.read()

            # 3. Attach the generated XSL file to the new fields on the current record
            client_name_safe = self.client_parent_id.name.replace(' ', '_').replace('/', '_')
            date_str = self.from_date.strftime('%Y%m')
            filename = "Generated_Payroll_%s_%s.xlsx" % (client_name_safe, date_str)

            self.write({
                'generated_payroll_document': base64.b64encode(excel_data),
                'generated_payroll_filename': filename,
            })
            
            # 4. *** NEW STEP: Update the state of the salary tracking records ***
            salary_records.write({'state': 'submit_to_payroll'})

            # Post a message to the chatter
            self.message_post(body=_("Payroll file '%s' successfully generated and attached. %d employee records moved to 'Submit to Payroll'.") % (filename, len(salary_records)))

            # 5. Return an action to force the client to reload the form
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
    
    def action_submit_to_payroll(self):
        # This method can be used for re-submission if the state is not 'draft'
        if not self.approval_payslip_document and not self.generated_payroll_document:
            raise UserError(_("Please upload or generate the Approval Payroll Document before submission."))
        for rec in self:
                rec.state = 'submit_to_payroll'
                rec.processed_date = datetime.now()
        return True

    def action_submit_to_payroll_manager(self):
        if not self.payslip_documents_ids:
            raise UserError(_("Please upload at least one document in the 'Documents' session before submitting for approval."))
                 
        # 1. Update the Approval Record state
        self.write({'state': 'submit_to_payroll_manager', 'processed_date': datetime.now()})
            
        # 2. Update Salary Tracking Records state
        self._get_related_salary_records().write({'state': 'submit_to_payroll_manager'}) # Assuming HR Manager is equivalent to Payroll Manager in salary tracking flow

        return True

    def action_submit_to_payroll_employee(self):
        # 1. Update the Approval Record state
        self.write({'state': 'submit_to_payroll_employee', 'processed_date': datetime.now()})
            
        # 2. Update Salary Tracking Records state
        self._get_related_salary_records().write({'state': 'submit_to_payroll_employee'}) # Assuming Payroll Employee is equivalent to HR Employee in salary tracking flow

        return True

    def action_reviewed_by_payroll_employee(self):
        # 1. Update the Approval Record state
        self.write({'state': 'done', 'processed_date': datetime.now()})
            
        # 2. Update Salary Tracking Records state
        self._get_related_salary_records().write({'state': 'done'})

        return True

class ClientPayslipRefuseWizard(models.TransientModel):
    _name = 'client.payslip.refuse.wizard'
            