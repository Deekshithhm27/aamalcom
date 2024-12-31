from odoo import models, fields, api


class EmployeeSponsor(models.Model):
    _name = 'employee.sponsor'
    _description = 'Employee Sponsor'

    name = fields.Char(string="Name",compute='_compute_name',store=True)
    sponsor_no = fields.Char(string="Sponsor No", required=True, size=10)
    company_name = fields.Char(string="Company Name", required=True)

    @api.depends('sponsor_no', 'company_name')
    def _compute_name(self):
        """ Compute the 'name' as a combination of sponsor_no and company_name """
        for record in self:
            if record.sponsor_no and record.company_name:
                record.name = f"{record.sponsor_no} - {record.company_name}"
            else:
                record.name = ''
