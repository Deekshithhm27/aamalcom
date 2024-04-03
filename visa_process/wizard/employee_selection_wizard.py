from odoo import models, fields

class EmployeeSelectionWizard(models.TransientModel):
    _name = 'employee.selection.wizard'
    _description = 'Employee Selection Wizard'

    department_ids = fields.Many2many('hr.department','selection_dept_ids',string="Department")
    employee_id = fields.Many2one('hr.employee', string='Employee',domain="[('department_id','=',department_ids)]")
    assign_type = fields.Selection([('assign','Assign'),('reassign','Reassign')],string="Employee assign Type",default='assign')
    levels = fields.Selection([('level1','Level 1'),('level2','Level 2')],string="Level of allocation")
    

    def apply_selected_employee(self):
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        if self.assign_type == 'assign':
            if self.employee_id:
                if active_enquiry.service_request == 'new_ev':
                    if active_enquiry.self_pay == True:
                        if active_enquiry.state in ('submitted') and active_enquiry.assigned_govt_emp_one == False:
                            active_enquiry.first_govt_employee_id = self.employee_id.id
                            active_enquiry.assigned_govt_emp_one = True
                    else:
                        if active_enquiry.state in ('approved') and active_enquiry.assigned_govt_emp_one == False:
                            active_enquiry.first_govt_employee_id = self.employee_id.id
                            active_enquiry.assigned_govt_emp_one = True
                        else:
                            active_enquiry.second_govt_employee_id = self.employee_id.id
                            active_enquiry.assigned_govt_emp_two = True
                    if active_enquiry.state in ('payment_done') and active_enquiry.assigned_govt_emp_one == True and active_enquiry.assigned_govt_emp_two == False:
                        active_enquiry.second_govt_employee_id = self.employee_id.id
                        active_enquiry.assigned_govt_emp_two = True
                else:
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
        else:
            if self.levels == 'level1':
                active_enquiry.first_govt_employee_id = self.employee_id.id
            else:
                active_enquiry.second_govt_employee_id = self.employee_id.id


        return {'type': 'ir.actions.act_window_close'}



# this is perfect
# approval process is only set for when fees to be paid by aamalcom. 
#   in this case Almaha cant request for payment confirmation (mentioned in mail)
#       instead almaha can upload documents and submit for review. once the documents are reviewd by project manager
        # process will be completed (because for EV there is not 2nd time document upload)