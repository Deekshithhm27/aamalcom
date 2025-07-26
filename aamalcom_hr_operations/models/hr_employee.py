from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_change_request_count = fields.Integer(
        string='Change Requests',
        compute='_compute_employee_change_request_count')

    def _compute_employee_change_request_count(self):
        change_request_model = self.env['hr.employee.change.request']
        for employee in self:
            count = change_request_model.search_count([('employee_id', '=', employee.id)])
            employee.employee_change_request_count = count