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
    salary_increase = fields.Monetary(string="Salary Increase",currency_field='currency_id')
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
                    raise ValidationError('Please add salary amount.')
    @api.model
    def update_pricing(self):  
        super(ServiceEnquiry, self).update_pricing()  
        for record in self:
            if record.service_request == 'salary_increase_process':
                pricing_id = self.env['service.pricing'].search([
                    ('service_request_type', '=', record.service_request_type),
                    ('service_request', '=', record.service_request)], limit=1)
                for p_line in pricing_id.pricing_line_ids:
                    if p_line.duration_id == record.employment_duration:
                        record.service_enquiry_pricing_ids.create({
                            'name': pricing_id.name,
                            'service_enquiry_id': record.id,
                            'service_pricing_id': pricing_id.id,
                            'service_pricing_line_id': p_line.id,
                            'amount': p_line.amount,
                            'remarks': p_line.remarks
                        })
                if record.salary_increase > 0:
                    record.service_enquiry_pricing_ids.create({
                        'name': 'Salary Increase',
                        'amount': record.salary_increase,
                        'service_enquiry_id': record.id,
                    })
    
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
                # Dynamic level based on state and assigned_govt_emp_two
                department_ids = []
                if line.state == 'submitted':
                    level = 'level1'
                if line.state == 'doc_uploaded_by_first_govt_employee' and not line.assigned_govt_emp_two:
                    level = 'level2'
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
                if record.upload_gosi_doc and not record.gosi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for GOSI Doc")
                record.state = 'waiting_payroll_approval'
                record.dynamic_action_status = "Documents Uploaded by second govt employee.Payroll Dept needs to close the ticket"
                # record.action_user_id=record.approver_id.user_id.id
    
    def action_process_complete_salary_increase(self):
        for record in self:
            if record.service_request == 'salary_increase_process':
                if record.upload_stating_doc and not record.stating_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Stating Doc")
                        # --- START OF NEW SALARY UPDATE LOGIC ---
                    if not record.employee_id:
                        raise UserError(_("Cannot process salary increase: Employee not linked to this service request."))

                    # Find the active contract for the employee
                    # 'state' = 'open' is standard for active contracts in hr.contract
                    # order='date_start desc' to get the latest contract if multiple are 'open' (though usually only one should be)
                    contract = self.env['hr.contract'].search([
                        ('employee_id', '=', record.employee_id.id),
                        ('state', '=', 'open') # Check your hr.contract states if 'open' is correct for active
                    ], limit=1, order='date_start desc')

                    if not contract:
                        _logger.warning(f"No active contract found for employee {record.employee_id.name} ({record.employee_id.id}) to update salary.")
                        raise UserError(_(f"Cannot update salary: No active contract found for employee '{record.employee_id.name}'. Please ensure the employee has an active contract."))

                    # Update the wage on the contract
                    # IMPORTANT: This will *add* the salary_increase to the current wage.
                    # If salary_increase is meant to be the *new total wage*, change to: contract.wage = record.salary_increase
                    old_wage = contract.wage
                    new_wage = old_wage + record.salary_increase

                    try:
                        contract.write({
                            'wage': new_wage,
                            # If you need to log the effective date of the new wage on the contract
                            # 'date_start': fields.Date.today(), # This would effectively restart the contract duration
                            # Consider if you need to create a new contract instead of updating existing one
                        })
                        # Update the custom field on hr.employee for last salary increase date
                        record.employee_id.write({
                            'x_last_salary_increase_date': date.today(),
                            # If you added x_last_salary_increase_amount
                            # 'x_last_salary_increase_amount': record.salary_increase,
                        })
                        _logger.info(f"Salary for {record.employee_id.name} updated from {old_wage} to {new_wage} via Salary Increase Process {record.name}.")
                        # Optional: Notify the user in the UI
                        self.env.user.notify_success(message=_("Salary successfully updated for {} to {}!").format(record.employee_id.name, new_wage))

                    except Exception as e:
                        _logger.error(f"Failed to update salary for employee {record.employee_id.name} from service enquiry {record.name}: {e}")
                        raise UserError(_(f"Failed to update salary due to an internal error. Please contact administrator. Error: {e}"))

                    # --- END OF NEW SALARY UPDATE LOGIC ---

                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False


    
