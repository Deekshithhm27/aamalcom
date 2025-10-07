from odoo import models, fields, api

class TerminationEmployeeWizard(models.TransientModel):
    _name = 'termination.assign.employee.wizard'
    _description = 'Assign Employee for Terminations'

    department_id = fields.Many2one(
        'hr.department', string="Department", required=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        domain="[('department_id', '=', department_id)]",
        required=True
    )

    @api.model
    def default_get(self, fields_list):
        """Set default department based on termination state."""
        res = super(TerminationEmployeeWizard, self).default_get(fields_list)
        termination = self.env['termination.request'].browse(self._context.get('active_id'))
        if termination:
            if termination.state == 'submit':
                hr_dept = self.env['hr.department'].search([('name', '=', 'HR')], limit=1)
                if hr_dept:
                    res['department_id'] = hr_dept.id
            elif termination.state == 'approved_by_pm':
                govt_dept = self.env['hr.department'].search([('name', '=', 'Government')], limit=1)
                if govt_dept:
                    res['department_id'] = govt_dept.id
        return res

    def action_apply(self):
        self.ensure_one()
        termination = self.env['termination.request'].browse(self._context.get('active_id'))
        if not termination:
            return

        # Change state based on current state
        if termination.state == 'submit':
            termination.write({'state': 'submitted_to_hr'})
        elif termination.state == 'approved_by_pm':
            termination.write({'state': 'submitted_to_gre'})
