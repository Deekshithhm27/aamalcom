from odoo import models


class EmployeeSelectionWizard(models.TransientModel):
    _inherit = 'employee.selection.wizard'

    def apply_selected_employee(self):
        result = super(EmployeeSelectionWizard, self).apply_selected_employee()
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        if active_enquiry and active_enquiry.service_request == 'exit_reentry_issuance' and self.assign_type == 'assign' and self.employee_id:
            if active_enquiry.aamalcom_pay == True:
                if active_enquiry.state == 'approved' and self.levels == 'level1':
                    active_enquiry.first_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_one = True
                    active_enquiry.assign_govt_emp_two = False 
            else:
                if active_enquiry.state == 'approved' and self.levels == 'level1':
                    active_enquiry.first_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_one = True
                    active_enquiry.assign_govt_emp_two = False 
        elif if active_enquiry.service_request == 'exit_reentry_issuance_ext':
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
