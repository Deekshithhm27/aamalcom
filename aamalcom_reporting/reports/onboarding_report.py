from odoo import models, api, fields
from datetime import datetime

class OnboardingReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.onboarding_report_template'
    _description = 'Onboarding Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        client_id = data.get('client_id')

        # Convert string dates to date objects for comparison if they are strings
        if isinstance(from_date, str):
            from_date = fields.Date.from_string(from_date)
        if isinstance(to_date, str):
            to_date = fields.Date.from_string(to_date)
        
        client = self.env['res.partner'].browse(client_id)

        # Corrected values based on your HrEmployee model
        employee_model_name = 'hr.employee' 
        client_link_field = 'client_parent_id' 
        date_of_joining_field = 'doj' 

        employee_model = self.env[employee_model_name]

        # Construct the domain
        domain = [
            (client_link_field, '=', client_id),
            (date_of_joining_field, '>=', from_date),
            (date_of_joining_field, '<=', to_date),
        ]

        employees = employee_model.search(domain)
        
        report_data = [{
            'client': client,
            'employees': employees,
        }]

        return {
            'doc_ids': docids,
            'doc_model': 'onboarding.report.wizard',
            'docs': report_data,
            'data': data,
            'from_date': from_date,
            'to_date': to_date,
            'client_name': client.name,
        }