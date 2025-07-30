from odoo import models, fields

class AssignEmployeeWizard(models.TransientModel):
    _name = 'assign.employee.wizard'
    _description = 'Assign Employee Wizard'

    department_ids = fields.Many2many('hr.department','assign_dept_ids',string="Department")
    employee_id = fields.Many2one('hr.employee', string='Employee',domain="[('department_id','=',department_ids)]")
    assign_type = fields.Selection([('assign','Assign'),('reassign','Reassign')],string="Employee assign Type",default='assign')
    levels = fields.Selection([('level1','Level 1')],string="Level of allocation",default='level1')
    

    def apply_selected_employee(self):
        active_enquiry = self.env['service.enquiry'].browse(self._context.get('active_id'))
        departments = self.department_ids.mapped('name')
        if departments:
            department_names = ', '.join(departments)
            active_enquiry.dynamic_action_status = (
                f"Documents upload pending by employee from {department_names} department."
            )
            active_enquiry.action_user_id = self.employee_id.user_id.id
            active_enquiry.state = 'coc_mofa_document'
        
        if self.employee_id:
            # Assign to govt_employee_id for all service requests
            active_enquiry.govt_employee_id = self.employee_id.id
            active_enquiry.first_assigned_govt_emp = True

        return {'type': 'ir.actions.act_window_close'} 