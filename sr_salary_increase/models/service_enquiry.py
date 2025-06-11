from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

    service_request = fields.Selection(
        selection_add=[
            ('salary_increase_process', 'Salary Increase Process')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'salary_increase_process': 'cascade'}

    )

    year_of_service = fields.Char(string="Service Period", readonly=True, compute="_compute_service_period")
    salary_increase = fields.Monetary(string="Expected Salary Increase",currency_field='currency_id')
    upload_stating_doc = fields.Binary(string="Upload Stating Document")
    upload_stating_doc_file_name = fields.Char(string="Stating Document")
    stating_doc_ref = fields.Char(string="Ref No.*")

    #To auto-populate doj from master records
    @api.onchange('employee_id')
    def onchange_employee_update_data(self):
        for line in self:
            line.doj = line.employee_id.doj

    #To calculate year of service from doj 
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
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'salary_increase_process':
                if not line.salary_increase:
                    raise ValidationError('Please add excepted salary amount.')
    
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

    def action_first_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_qiwa_doc and not record.qiwa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Doc")
                record.state = 'doc_uploaded_by_first_govt_employee'
                record.dynamic_action_status = "Documents Uploaded by first govt employee. Second govt employee need to be assigned by PM"
                record.action_user_id=record.approver_id.user_id.id

    def action_second_govt_emp_submit_salary(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_gosi_doc and not record.qiwa_gosi_ref:
                    raise ValidationError("Kindly Update Reference Number for GOSI Doc")
                record.state = 'waiting_payroll_approval'
                # record.dynamic_action_status = "Documents Uploaded by first govt employee. Second govt employee need to be assigned by PM"
                # record.action_user_id=record.approver_id.user_id.id
    
    def open_assign_employee_wizard(self):
        for line in self:
            if line.service_request == 'salary_increase_process':
                # Dynamic level based on state and assigned_govt_emp_two
                department_ids = []
                if line.state == 'approved':
                    level = 'level1'
                if line.state == 'doc_uploaded_by_first_govt_employee' and not line.assigned_govt_emp_two:
                    level = 'level1'
                if line.state == 'doc_uploaded_by_first_govt_employee' and line.assigned_govt_emp_two:
                    level = 'level2'
                # Sorting and picking department line based on level
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

    def action_process_complete(self):
        result = super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_stating_doc and not record.stating_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Stating Doc")
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
        return result


    
