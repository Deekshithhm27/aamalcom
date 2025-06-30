# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class EmployeeSelectionWizardInherit(models.TransientModel):
    _inherit = 'employee.selection.wizard' 

    def apply_selected_employee(self):
        super(EmployeeSelectionWizardInherit, self).apply_selected_employee()
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        if active_enquiry and active_enquiry.service_request == 'final_clearance' and self.assign_type == 'assign' and self.employee_id:
            if active_enquiry.state == 'submitted' and self.levels == 'level1':
                active_enquiry.first_govt_employee_id = self.employee_id.id
                active_enquiry.assigned_govt_emp_one = True
                active_enquiry.assign_govt_emp_two = False 
            elif active_enquiry.state == 'doc_uploaded_by_first_govt_employee' and self.levels == 'level2' and not active_enquiry.assigned_govt_emp_two:
                active_enquiry.second_govt_employee_id = self.employee_id.id
                active_enquiry.assigned_govt_emp_two = True 
                active_enquiry.assign_govt_emp_two = True 
                
            
            