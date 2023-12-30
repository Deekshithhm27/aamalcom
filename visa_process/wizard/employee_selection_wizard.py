from odoo import models, fields

class EmployeeSelectionWizard(models.TransientModel):
    _name = 'employee.selection.wizard'
    _description = 'Employee Selection Wizard'

    department_ids = fields.Many2many('hr.department','selection_dept_ids',string="Department")
    employee_id = fields.Many2one('hr.employee', string='Employee',domain="[('department_id','=',department_ids)]")
    

    def apply_selected_employee(self):
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        if self.employee_id:
            if active_enquiry.state in ('submitted','waiting_gm_approval','waiting_op_approval','waiting_fin_approval'):
                active_enquiry.first_govt_employee_id = self.employee_id.id
                active_enquiry.assigned_govt_emp_one = True
            if active_enquiry.state in ('payment_done','approved'):
                if active_enquiry.service_request == 'iqama_card_req' and active_enquiry.state == 'payment_done':
                    active_enquiry.first_govt_employee_id = self.employee_id.id
                    active_enquiry.assigned_govt_emp_one = True
                else:
                    active_enquiry.second_govt_employee_id = self.employee_id.id
                    # active_enquiry.first_govt_employee_id = False
                    active_enquiry.assigned_govt_emp_two = True
        return {'type': 'ir.actions.act_window_close'}
