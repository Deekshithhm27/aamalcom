from odoo import models, fields, api
from odoo.exceptions import UserError

class InsuranceReimbursement(models.Model):
    _inherit = 'hr.employee'

    dependent_ids = fields.One2many('employee.dependents','employee_id',string="Dependents")

    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_silver+','SILVER+'),('class_silver','SILVER'),('class_a+','A+'),('class_a','A'),('class_b+','B+'),('class_b','B'),('class_c','C'),('class_e','E')],string="Insurance Class",tracking=True)


class EmployeeDependents(models.Model):
    _name = "employee.dependents"

    name = fields.Char(string="Name")
    member_id = fields.Char(string="Membership Id")
    employee_id = fields.Many2one('hr.employee',string="Employee")