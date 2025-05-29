from odoo import models, fields

class EmployeeSelectionWizardInherit(models.TransientModel):
    _inherit = 'employee.selection.wizard'

    def apply_selected_employee(self):
        """Override apply_selected_employee to add assigned_department_id logic."""
        
        res = super(EmployeeSelectionWizardInherit, self).apply_selected_employee()  # Call parent logic first

        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        
        if active_enquiry.service_request == 'general_query' and self.employee_id:
            active_enquiry.assigned_department_id = self.employee_id.department_id.id
            
            if active_enquiry.assigned_department_id:
                active_enquiry.dynamic_action_status = (
                    f"Documents upload pending by employee from {active_enquiry.assigned_department_id.name} department."
                )
                active_enquiry.action_user_id =self.employee_id.user_id.id

        return res
