from odoo import models, fields, api, _
from datetime import date # Import date for fields.Date.today()

class EmpSalaryLinesExtension(models.Model):
    _inherit = "emp.salary.line" # Inherit the existing emp.salary.line model
    _description = "Employee Salary Line Extension for SR Salary Increase"

    
    last_update_date = fields.Date(string="Last Updated On", help="Date when this salary component was last updated.")

    @api.model
    def write(self, vals):
        # Check if 'amount' is one of the fields being updated
        if 'amount' in vals:
            # Set 'last_update_date' to today's date
            vals['last_update_date'] = fields.Date.today()
        # Call the original write method of the inherited model
        return super(EmpSalaryLinesExtension, self).write(vals)

    # Override the create method to automatically set the date on new records
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # If 'amount' is provided and 'last_update_date' is not explicitly set, set it to today
            if 'amount' in vals and 'last_update_date' not in vals:
                vals['last_update_date'] = fields.Date.today()
        # Call the original create method of the inherited model
        return super(EmpSalaryLinesExtension, self).create(vals_list)

