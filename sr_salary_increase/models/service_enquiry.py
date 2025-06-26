from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[('salary_increase_process', 'Salary Increase Process')],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'salary_increase_process': 'cascade'}
    )
    employee_id = fields.Many2one('hr.employee', string='Employee')
    client_salary_rule_ids = fields.One2many('se.emp.salary.line', 'service_enquiry_id', string="Salary Structure")
    year_of_service = fields.Char(string="Service Period", readonly=True, compute="_compute_service_period")
    salary_increase = fields.Monetary(string="Salary Increase", currency_field='currency_id')
    upload_stating_doc = fields.Binary(string="Upload Stating Document")
    upload_stating_doc_file_name = fields.Char(string="Stating Document")
    stating_doc_ref = fields.Char(string="Ref No.*")

    @api.onchange('employee_id')
    def onchange_employee_update_data(self):
        for line in self:
            if line.employee_id: 
                line.doj = line.employee_id.doj
            else:
                line.doj = False 

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

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'salary_increase_process':
                if not line.salary_increase:
                    raise ValidationError('Please add salary amount.')

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
                record.send_email_to_op()

    def open_assign_employee_wizard(self):
        for line in self:
            if line.service_request == 'salary_increase_process':
                department_ids = []
                level = ''
                if line.state == 'submitted':
                    level = 'level1'
                if line.state == 'doc_uploaded_by_first_govt_employee' and not line.assigned_govt_emp_two:
                    level = 'level2'
                if line.state == 'doc_uploaded_by_first_govt_employee' and line.assigned_govt_emp_two:
                    level = 'level2'
                req_lines = line.service_request_config_id.service_department_lines
                sorted_lines = sorted(req_lines, key=lambda l: l.sequence)
                for lines in sorted_lines:
                    if level == 'level1':
                        department_ids.append((4, lines.department_id.id))
                        break
                    elif level == 'level2' and lines.sequence == 2:
                        department_ids.append((4, lines.department_id.id))
                        break
                return {
                    'name': 'Select Employee',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.selection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_department_ids': department_ids,
                        'default_assign_type': 'assign',
                        'default_levels': level,
                    },
                }
        return super(ServiceEnquiry, self).open_assign_employee_wizard()

    def action_first_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_qiwa_doc and not record.qiwa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Doc")
                record.state = 'doc_uploaded_by_first_govt_employee'
                record.dynamic_action_status = "Documents Uploaded by first govt employee. Second govt employee need to be assigned by PM"
                record.action_user_id = record.approver_id.user_id.id

    def action_second_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_gosi_doc and not record.gosi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for GOSI Doc")
                record.state = 'waiting_payroll_approval'
                record.dynamic_action_status = "Documents Uploaded by second govt employee. Payroll Dept needs to close the ticket"
                group = self.env.ref('visa_process.group_service_request_payroll_manager')
                users = group.users
                employee = self.env['hr.employee'].search([
                ('user_id', 'in', users.ids)
                ], limit=1)
                record.action_user_id = employee.user_id

    def action_process_complete_salary_increase(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_stating_doc and not record.stating_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Stating Doc")
                # Validate if an employee is linked to the service request
                if not record.employee_id:
                    raise ValidationError("No employee linked to this service request. Cannot update salary.")
                # Validate if the salary increase amount is provided and positive
                if not record.salary_increase or record.salary_increase <= 0:
                    raise ValidationError("Salary Increase amount must be a positive value to apply an increase.")
                # ---Custom Salary Update Logic ---
                employee = record.employee_id
                basic_salary_rule = self.env['hr.client.salary.rule'].search([('code', '=', 'Basic')], limit=1)
                if not basic_salary_rule:
                    basic_salary_rule = self.env['hr.client.salary.rule'].search([('name', '=', 'Basic')], limit=1)
                if not basic_salary_rule:
                    raise ValidationError(
                        "The 'Basic' salary structure type (hr.client.salary.rule) was not found. "
                        "Please ensure a salary rule with 'Code' or 'Name' as 'Basic' exists in your system."
                    )
                existing_basic_salary_line = employee.client_salary_rule_ids.filtered(
                    lambda line: line.name.id == basic_salary_rule.id
                )
                if existing_basic_salary_line:
                    # Get the current basic salary
                    current_basic_salary = existing_basic_salary_line.amount
                    # Calculate the new basic salary by ADDING the increase
                    new_basic_salary = current_basic_salary + record.salary_increase

                    # Update the existing 'Basic' salary line with the new calculated amount
                    existing_basic_salary_line.write({'amount': new_basic_salary})
                    # Log the update in the chatter of the service request
                    record.message_post(body=f"Updated Basic Salary for employee "
                                           f"<b>{employee.name}</b> from {current_basic_salary} {record.currency_id.symbol} "
                                           f"to <b>{new_basic_salary} {record.currency_id.symbol}</b> "
                                           f"(+{record.salary_increase} {record.currency_id.symbol} increase) "
                                           f"from Service Request <b>{record.name}</b>.")
                record.state = 'done'
                record.dynamic_action_status = "Process Completed"
                record.action_user_id = False



class EmpSalaryLines(models.Model):
    _name = "se.emp.salary.line" 
    _order = 'sequence asc'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _description = "Employee Salary Line for Service Enquiry"

    name = fields.Many2one('hr.client.salary.rule',string="Structure Type")
    sequence = fields.Integer(string="Sequence",related="name.sequence",store=True)

    service_enquiry_id = fields.Many2one('service.enquiry',string="Service Enquiry") # Corrected model name
    amount = fields.Float(string="Amount")
