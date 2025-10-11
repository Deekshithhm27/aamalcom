from odoo import fields, models, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import base64
import io
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class HrPayrollApproval(models.Model):
    _name = 'hr.payroll.approval'
    _description = 'Payslip Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Payslip Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.payroll.approval')
    )
    employee_id = fields.Many2one('hr.employee', string='Employee')  
    date_from = fields.Date(string='Date From', required=True, readonly=True,
                             states={'draft': [('readonly', False)]}, 
                             default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', required=True, readonly=True,
                           states={'draft': [('readonly', False)]},
                           default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_to_payroll', 'Submitted for Verification'),
        ('submit_to_payroll_employee', 'Submitted to Payroll Employee'), # Unused in this flow, but kept for schema
        ('submit_to_payroll_manager', 'Submitted to Payroll Manager'),
        ('approved', 'Approved'),
        ('done', 'Approved Authorized Confirmed'),
    ], string="Status", default='draft', tracking=True)
    upload_payroll_document = fields.Binary(string="Payroll Document")
    generated_payroll_document = fields.Binary(string="Generated Payroll Document", readonly=True)
    generated_payroll_filename = fields.Char(string="Generated Filename", readonly=True)
    processed_date = fields.Datetime(string="Processed Date", readonly=True, copy=False)

    

    def _get_payslips_in_range(self, states=None):
        """ to find hr.payslip records in the date range, optionally filtering by state."""
        # Domain strictly enforces the date range of the approval record
        domain = [
            ('date_from', '=', self.date_from),
            ('date_to', '=', self.date_to),
        ]
        if states:
             domain.append(('state', 'in', states))
        return self.env['hr.payslip'].search(domain)
        
    def _synchronize_payslip_run(self, payslips, target_state):
        """
        Updates the state of hr.payslip.run batches directly.
        It only changes the state if the new state is further along than the current one.
        """
        runs = payslips.mapped('payslip_run_id').exists()
        
        if not runs:
            return
        # Define state order for comparison (ensure this matches hr.payslip.run states)
        STATE_ORDER = {
            'draft': 0,
            'submit_to_payroll': 1, 
            'submit_to_payroll_employee': 2,
            'submit_to_payroll_manager': 3,
            'approved': 4,
            'done': 5,
        }
        target_order = STATE_ORDER.get(target_state, 0)
        # Filter runs: only update if the run's current state is less advanced than the target state
        runs_to_update = self.env['hr.payslip.run']
        for run in runs:
            current_order = STATE_ORDER.get(run.state, 0)
            if target_order > current_order:
                runs_to_update += run
        # 2. Update the state of the filtered runs
        if runs_to_update:
            runs_to_update.write({'state': target_state})


    # --- BUTTON ACTIONS ---

    def action_generate_payslip(self):
        """Generates XLSX report and moves payslips/runs to 'submit_to_payroll' (First step)."""
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_("The 'xlsxwriter' library is required to generate the report. Please install it."))
        if not self.date_from or not self.date_to:
            raise UserError(_("Please ensure From Date and To Date are set."))
        # Find ALL target hr.payslip records in any state for reporting (Validation done inside)
        payslip_records = self._get_payslips_in_range()
        if not payslip_records:
            raise UserError(_("Validation Error: No Payslip records found in the period **%s to %s**. Cannot generate the report.") % (
                self.date_from, self.date_to))
        # 1. Generate the consolidated XLSX report
        report_data, filename = self._generate_payslip_xlsx_data(payslip_records)
        # 2. Attach the report
        self.write({
            'generated_payroll_document': base64.b64encode(report_data),
            'generated_payroll_filename': filename,
            # Update approval record state to indicate generation is done and ready for verification
            'state': 'submit_to_payroll', 
            'processed_date': datetime.now() # FIX 1: Use correct datetime.now()
        })
        # 3. Update the state of ALL found hr.payslip records and their runs
        # We only move the payslips/runs if they are still in draft
        draft_payslips = self._get_payslips_in_range(states=['draft'])
        draft_payslips.write({'state': 'submit_to_payroll', 'processed_date': datetime.now()})
        self._synchronize_payslip_run(draft_payslips, 'submit_to_payroll')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Consolidated Payslip Batch report generated and attached. **%s** payslip(s) status updated to "Submitted for Verification".') % len(draft_payslips),
                'type': 'success',
                'sticky': False,
            }
        }
    
    # Button to move from DRAFT/SUBMIT_TO_PAYROLL to SUBMITTED TO PAYROLL MANAGER
    def action_submit_for_approval(self):
        """Updates state to 'submit_to_payroll_manager' for payslips and runs."""
        payslips = self._get_payslips_in_range(states=['submit_to_payroll']) 
        if not payslips:
            raise UserError(_("No Payslips found in 'Submitted for Verification' state for this period. Cannot submit for manager approval."))
        # 1. Update Payslip State
        payslips.write({'state': 'submit_to_payroll_manager', 'processed_date': datetime.now()}) 
        # 2. SYNCHRONIZE: Update all associated Payslip Runs
        self._synchronize_payslip_run(payslips, 'submit_to_payroll_manager')
        # 3. Update Approval Record State
        self.write({'state': 'submit_to_payroll_manager', 'processed_date': datetime.now()}) 
        return True


    # Button for the Manager to APPROVE
    def action_submit_to_payroll_employee(self):
        """Updates state from 'submit_to_payroll_manager' to 'approved' for payslips and runs."""
        payslips = self._get_payslips_in_range(states=['submit_to_payroll_manager'])
        if not payslips:
            raise UserError(_("No Payslips found in 'Submitted to Payroll Manager' state for this period. Cannot Approve."))
        # 1. Update Payslip State to 'approved'
        payslips.write({'state': 'approved', 'processed_date': datetime.now()}) 
        # 2. SYNCHRONIZE: Update all associated Payslip Runs
        self._synchronize_payslip_run(payslips, 'approved')
        # 3. Update Approval Record State
        self.write({'state': 'approved', 'processed_date': datetime.now()}) 
        return True

    # ---  METHOD: XLSX REPORT GENERATION (BATCH) ---
    def _generate_payslip_xlsx_data(self, payslips):
            """Helper to create the consolidated XLSX report content with AamalCom format."""
            self.ensure_one()
            
            if not payslips:
                return b'', 'Empty_Payslip_Batch.xlsx'

            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet('Payslip Batch Report')

            # === Formats ===
            # Standard formats
            currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
            data_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
            
            # Header formats
            title_format = workbook.add_format({'bold': True, 'font_size': 18, 'align': 'center', 'valign': 'vcenter'})
            subtitle_format = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter'})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
            
            # --- Context Data ---
            # all payslips are for the same month, we use the first one for the title.
            first_payslip = payslips[0]
            period_str = first_payslip.date_from.strftime('%b - %Y').upper()
            company_name = self.env.user.company_id.name or 'AamalCom'

            # === Report Headers (Row 1 and 2) ===
            # We need to calculate the total number of columns for merging
            COLUMNS = [
                'Sl.No', 'Employee Name', 'Id', 'Nationality', 'IBAN', 'BANK', 'Total Salary', 
                'Days in months', 'Days Present', 'Overtime Hours', 'Basic Salary', 
                'Housing Allowance', 'Transport allowance', 'Other Allowance', 'Gross Salary', 
                'OT amount', 'Additions', 'Deduction GOSI', 'Deductions', 'Day discounts', 
                'Total Deductions', 'Net Salary', 'Mode of Payment', 'Company Name'
            ]
            
            num_cols = len(COLUMNS)
            
            # Row 1: Main Header (Merged)
            sheet.merge_range(0, 0, 0, num_cols - 1, f'{company_name} Company', title_format)
            
            # Row 2: Sub Header (Merged)
            sheet.merge_range(1, 0, 1, num_cols - 1, f'STAFF PAYROLL FOR THE MONTH OF {period_str}', subtitle_format)
            
            # Row 3: Column Headers
            col_map = {col: idx for idx, col in enumerate(COLUMNS)}
            
            for col_idx, name in enumerate(COLUMNS):
                sheet.write(2, col_idx, name, header_format)
                
            # === Data Mapping for Payslip Lines ===
            # Map requested column names to the corresponding Odoo Payslip Line code.
            # Use an empty string if you can't map it directly to a code.
            LINE_CODE_MAP = {
                'Basic Salary': 'BASIC',
                'Housing Allowance': 'HRA',         
                'Transport allowance': 'TRANSPORT', 
                'Other Allowance': 'OTHER',       
                'Gross Salary': 'GROSS',
                'OT amount': 'OT',                 
                'Additions': 'ADD',                 
                'Deduction GOSI': 'GOSI',
                'Deductions': 'DED',               
                'Day discounts': 'DAYDISCOUNT',    
                'Total Deductions': 'TOTALDEDUCTION', 
                'Net Salary': 'NET',
            }

            # === Data Rows ===
            row_num = 3
            for i, payslip in enumerate(payslips):
                emp = payslip.employee_id
                
                # Helper to get the total for a salary rule code (from hr.payslip.line)
                def get_payslip_line_amount(code):
                    line = payslip.line_ids.filtered(lambda l: l.code == code)
                    return line.total if line else 0.0

                # Helper to get the number of days/hours from worked_days_line
                def get_worked_days_value(line_type, field='number_of_days'):
                    # Assuming 'WORK100' is the code for days present
                    line = payslip.worked_days_line_ids.filtered(lambda l: l.code == line_type)
                    if line:
                        return line[field]
                    return 0

                # Helper to get the amount from input_line
                def get_input_line_amount(code):
                    line = payslip.input_line_ids.filtered(lambda l: l.code == code)
                    return line.amount if line else 0.0
                    
                
                # --- FETCHING CORE DATA ---
                
                days_in_month = (payslip.date_to - payslip.date_from).days + 1
                
                days_present = get_worked_days_value('WORK100', 'number_of_days') 

                overtime_hours = get_input_line_amount('OT_HOURS') / payslip.contract_id.wage # Placeholder logic, adjust as needed

                
                # Sl.No
                sheet.write(row_num, col_map['Sl.No'], i + 1, data_format) 
                
                # Employee Name (Combined name is safer than surname/given name if they are not used)
                sheet.write(row_num, col_map['Employee Name'], emp.name or '', data_format) 
                
                # Id (from hr.employee.client_emp_sequence)
                sheet.write(row_num, col_map['Id'], emp.client_emp_sequence or '', data_format) 
                
                # Nationality (from hr.employee.country_id.name)
                sheet.write(row_num, col_map['Nationality'], emp.country_id.name or '', data_format) 
                
                # IBAN and BANK (Requested to be blank)
                sheet.write(row_num, col_map['IBAN'], '', data_format)
                sheet.write(row_num, col_map['BANK'], '', data_format)
                
                # Total Salary (Using NET amount for Total Salary column as per common practice)
                sheet.write(row_num, col_map['Total Salary'], get_payslip_line_amount('NET'), currency_format)
                
                # Days in months, Days Present, Overtime Hours
                sheet.write(row_num, col_map['Days in months'], days_in_month, data_format)
                sheet.write(row_num, col_map['Days Present'], days_present, data_format)
                sheet.write(row_num, col_map['Overtime Hours'], overtime_hours, data_format)

                # Salary Lines - Use the map to dynamically fetch amounts
                for col_name, line_code in LINE_CODE_MAP.items():
                    if col_name in col_map:
                        amount = get_payslip_line_amount(line_code)
                        sheet.write(row_num, col_map[col_name], amount, currency_format)
                # You may need a field on hr.employee or hr.contract to store this
                sheet.write(row_num, col_map['Mode of Payment'], '', data_format) 
                
                # Company Name (AamalCom)
                sheet.write(row_num, col_map['Company Name'], company_name, data_format) 
                
                row_num += 1

            # Auto-set column widths for readability
            sheet.set_column(col_map['Employee Name'], col_map['Employee Name'], 30)
            sheet.set_column(col_map['Id'], col_map['Nationality'], 15)
            sheet.set_column(col_map['IBAN'], col_map['IBAN'], 25)
            sheet.set_column(col_map['Total Salary'], col_map['Net Salary'], 15)


            workbook.close()
            output.seek(0)
            
            filename = f"AamalCom_STAFF_PAYROLL_{first_payslip.date_from.strftime('%Y%m')}.xlsx"
            return output.read(), filename
    
    def action_payroll_approval_done(self):
        # NOTE: This should typically move from 'approved' to 'done'.
        payslips = self._get_payslips_in_range(states=['approved'])
        payslips.write({'state': 'done'})
        self._synchronize_payslip_run(payslips, 'done')
        return self.write({'state': 'done'})