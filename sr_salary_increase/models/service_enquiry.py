# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime # Import datetime for contract dates
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU # Import weekdays for relativedelta

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    employee_id = fields.Many2one('hr.employee', string='Employee')

    service_request = fields.Selection(
        selection_add=[('salary_increase_process', 'Salary Increase Update (Qiwa/GOSI)')],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'salary_increase_process': 'cascade'}
    )
    # This field already exists to hold the proposed salary breakup for the service request
    client_salary_rule_ids = fields.One2many('se.emp.salary.line', 'service_enquiry_id', string="Proposed Salary Breakup")
    
    year_of_service = fields.Char(string="Service Period", readonly=True, compute="_compute_service_period")
    upload_stating_doc = fields.Binary(string="Upload Stating Document")
    upload_stating_doc_file_name = fields.Char(string="Stating Document")
    stating_doc_ref = fields.Char(string="Ref No.*")

    @api.model
    def create(self, vals):
        """Handles file naming conventions while creating a record."""
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')
        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
        if 'upload_stating_doc' in vals:
            vals['upload_stating_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_StatingDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        """Ensures correct file naming conventions when updating records."""
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_stating_doc' in vals:
                vals['upload_stating_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_StatingDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)    

    @api.onchange('employee_id')
    def onchange_employee_update_data(self):
        """
        Original onchange method, now also calls the new method
        to populate salary lines on service request.
        """
        for line in self:
            if line.employee_id:
                line.doj = line.employee_id.doj
                # Call the new method to populate the salary lines
                line._onchange_employee_populate_salary_lines()
            else:
                line.doj = False
                # Clear existing salary lines if employee is unselected
                line.client_salary_rule_ids = [(5, 0, 0)] # Command to clear all existing lines

    @api.depends('employee_id', 'employee_id.doj')
    def _compute_service_period(self):
        for record in self:
            if record.employee_id and record.employee_id.doj:
                doj = record.employee_id.doj
                today = date.today()
                delta = relativedelta(today, doj)
                record.year_of_service = f"{delta.years} years, {delta.months} months"
            else:
                record.year_of_service = "N/A"

    def _onchange_employee_populate_salary_lines(self):
        """
        Populates the client_salary_rule_ids (se.emp.salary.line)
        with the employee's current salary structure (emp.salary.line).
        This provides a starting point for the client to modify the breakup.
        """
        self.ensure_one()
        if self.service_request != 'salary_increase_process':
            if not self.employee_id:
                self.client_salary_rule_ids = [(5, 0, 0)] # Clear lines if no employee
                return

            # Clear existing lines on the service request first to avoid duplicates
            self.client_salary_rule_ids = [(5, 0, 0)]

            # Iterate over the employee's current salary lines and create copies for the service request
            new_lines = []
            for emp_salary_line in self.employee_id.client_salary_rule_ids:
                new_lines.append((0, 0, {
                    'name': emp_salary_line.name.id, # Link to hr.client.salary.rule
                    'sequence': emp_salary_line.sequence,
                    'amount': emp_salary_line.amount,
                    # 'last_update_date': emp_salary_line.last_update_date, # Optional: copy this if you want it editable on SR
                }))
            self.client_salary_rule_ids = new_lines

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'salary_increase_process':
                if not line.client_salary_rule_ids: # Changed validation from salary_increase to client_salary_rule_ids
                    raise ValidationError('Please provide the salary breakup details.')
                

    def action_salary_increase_submit_for_approval(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                record.state = 'waiting_op_approval'
                group = self.env.ref('visa_process.group_service_request_operations_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                    ('user_id', 'in', users.ids)
                ], limit=1)
                record.dynamic_action_status = f"Waiting for approval by OM"
                record.action_user_id = employee.user_id
                record.write({'processed_date': fields.Datetime.now()})
                record.send_email_to_op()

    def open_assign_employee_wizard(self):
        """ super method to add a new condition for `exit_reentry_issuance_ext` service request. """
        result = super(ServiceEnquiry, self).open_assign_employee_wizard()
        for record in self:
            if record.service_request == 'salary_increase_process' and record.state == 'doc_uploaded_by_first_govt_employee':
                # level = 'level1'
                department_ids = []
                req_lines = record.service_request_config_id.service_department_lines
                sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
                for lines in sorted_lines:
                    # if level == 'level1':
                    department_ids.append((4, lines.department_id.id))
                record.write({'processed_date': fields.Datetime.now()})
                result.update({
                    'name': 'Select Employee',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.selection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_department_ids': department_ids,
                        'default_assign_type': 'assign',
                        'default_levels': 'level2',
                    },
                })
        return result



    def action_first_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_qiwa_doc and not record.qiwa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Doc")
                record.state = 'doc_uploaded_by_first_govt_employee'
                record.dynamic_action_status = "Documents Uploaded by first govt employee. Second govt employee need to be assigned by PM"
                record.action_user_id = record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})

    def action_second_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_gosi_doc and not record.gosi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for GOSI Doc")
                record.state = 'waiting_payroll_approval'
                record.dynamic_action_status = "Documents Uploaded by second govt employee. Payroll Dept needs to close the ticket"
                record.write({'processed_date': fields.Datetime.now()})
                # group = self.env.ref('visa_process.group_service_request_payroll_employee')
                # users = group.users
                # employee = self.env['hr.employee'].search([
                # ('user_id', 'in', users.ids)
                # ], limit=1)
                record.action_user_id = False


    def action_process_complete_salary_increase(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_stating_doc and not record.stating_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Stating Doc")
                
                employee = record.employee_id
                
                # --- NEW LOGIC: Update employee's main salary structure ---
                # 1. Clear existing salary lines on the employee record
                employee.client_salary_rule_ids = [(5, 0, 0)]
                
                # 2. Create new salary lines on the employee record based on the service enquiry's proposed lines
                new_employee_salary_lines = []
                for se_salary_line in record.client_salary_rule_ids:
                    new_employee_salary_lines.append((0, 0, {
                        'name': se_salary_line.name.id,
                        'sequence': se_salary_line.sequence,
                        'amount': se_salary_line.amount,
                        'employee_id': employee.id, # Ensure the link to the employee is set
                    }))
                employee.client_salary_rule_ids = new_employee_salary_lines
                # --- END NEW LOGIC ---

                # Now, call confirm_salary_details which will use the newly updated employee salary lines
                employee.confirm_salary_details()
                
                record.state = 'done'
                record.dynamic_action_status = "Process Completed"
                record.action_user_id = False
                record.write({'processed_date': fields.Datetime.now()})
                

class EmpSalaryLines(models.Model):
    _name = "se.emp.salary.line"
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Employee Salary Line for Service Enquiry"

    name = fields.Many2one('hr.client.salary.rule',string="Structure Type", required=True)
    sequence = fields.Integer(string="Sequence",related="name.sequence",store=True)

    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Enquiry")
    amount = fields.Float(string="Amount", required=True)