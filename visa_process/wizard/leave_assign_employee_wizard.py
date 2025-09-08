# leave_assign_employee_wizard.py
from odoo import models, fields, api

class LeaveAssignEmployeeWizard(models.TransientModel):
    _name = 'leave.assign.employee.wizard'
    _description = 'Assign Employee for Leave'

    department_id = fields.Many2one(
        'hr.department', string="Department", required=True
    )
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", domain="[('department_id', '=', department_id)]", required=True
    )

    def action_apply(self):
        self.ensure_one()
        # Change 'hr.leave' to 'visa.leave'
        leave = self.env['visa.leave'].browse(self._context.get('active_id'))
        if leave:
            # The employee field in visa.leave is 'employee_id'
            leave.write({'employee_id': self.employee_id.id, 'state': 'submitted_to_gre'})
