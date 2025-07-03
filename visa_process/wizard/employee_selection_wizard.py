from odoo import models, fields, _
from odoo.exceptions import ValidationError

class EmployeeSelectionWizard(models.TransientModel):
    _name = 'employee.selection.wizard'
    _description = 'Employee Selection Wizard'

    department_ids = fields.Many2many('hr.department','selection_dept_ids',string="Department")
    employee_id = fields.Many2one('hr.employee', string='Employee',domain="[('department_id','in',department_ids)]") # Changed to 'in' for many2many
    assign_type = fields.Selection([('assign','Assign'),('reassign','Reassign')],string="Employee assign Type",default='assign')
    levels = fields.Selection([('level1','Level 1'),('level2','Level 2')],string="Level of allocation")


    def apply_selected_employee(self):
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))

        if not active_enquiry:
            raise ValidationError(_("No active service enquiry found."))
        if not self.employee_id:
            raise ValidationError(_("Please select an employee to assign."))


        departments = self.department_ids.mapped('name')
        if departments:
            department_names = ', '.join(departments)
            active_enquiry.dynamic_action_status = (
                f"Documents upload pending by employee from {department_names} department."
            )
            active_enquiry.action_user_id = self.employee_id.user_id.id

        if self.assign_type == 'assign':
            if active_enquiry.service_request == 'hr_card':
                if active_enquiry.self_pay:
                    # Self Pay Logic for HR Card (assignment in payment_done state for both)
                    if self.levels == 'level1':
                        active_enquiry.first_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
                        # If the next assignment is for the second employee immediately after the first in the same state,
                        # you might want to consider a quick re-trigger of the wizard or handle it differently if it's always sequential.
                        # For now, this assigns the first. The button logic in XML will handle when the second can be assigned.
                    elif self.levels == 'level2':
                        active_enquiry.second_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_two = True
                else:
                    # Not Self Pay Logic for HR Card
                    if self.levels == 'level1':
                        active_enquiry.first_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
                    elif self.levels == 'level2':
                        active_enquiry.second_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_two = True
            elif active_enquiry.service_request == 'new_ev':
                if active_enquiry.self_pay == True:
                    if self.levels == 'level1': # Assuming level1 corresponds to first employee assignment
                        active_enquiry.first_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
                    elif self.levels == 'level2': # Assuming level2 corresponds to second employee assignment
                        active_enquiry.second_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_two = True
                else: # new_ev, not self_pay
                    if self.levels == 'level1':
                        active_enquiry.first_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_one = True
                    elif self.levels == 'level2':
                        active_enquiry.second_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_two = True
            elif active_enquiry.service_request == 'iqama_card_req':
                # Original logic for iqama_card_req: always assigns to first_govt_employee_id
                # if self.levels == 'level1': # Based on your service_enquiry.py, iqama_card_req only gets level1 at payment_done.
                    active_enquiry.first_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_one = True
                # If there's a second level for iqama_card_req in the future, you'd add an elif self.levels == 'level2': here
            else: # For other service requests where level1 and level2 apply generally
                if self.levels == 'level1':
                    active_enquiry.first_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_one = True
                elif self.levels == 'level2':
                    active_enquiry.second_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_two = True

        else: # Reassign logic
            if self.levels == 'level1':
                active_enquiry.first_govt_employee_id = self.employee_id.id
            else:
                active_enquiry.second_govt_employee_id = self.employee_id.id

        return {'type': 'ir.actions.act_window_close'}