from odoo import models


class EmployeeSelectionWizard(models.TransientModel):
    _inherit = 'employee.selection.wizard'

    def apply_selected_employee(self):
        result = super(EmployeeSelectionWizard, self).apply_selected_employee()
        for record in self:
            active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
            departments = self.department_ids.mapped('name')
            department_names = ', '.join(departments)
            if active_enquiry.service_request == 'exit_reentry_issuance_ext':
                if record.assign_type == 'assign' and record.employee_id:
                    # if active_enquiry.state == 'submitted':
                    if not active_enquiry.aamalcom_pay:
                        active_enquiry.dynamic_action_status = (
                            f"Review and request payment confirmation pending by employee from {department_names} department."
                        )
                        active_enquiry.first_govt_employee_id = record.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
                    else:
                        active_enquiry.first_govt_employee_id = record.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
        return result
