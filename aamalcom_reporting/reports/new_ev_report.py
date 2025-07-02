# aamalcom_reporting/reports/new_ev_report.py

import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class NewEvReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.new_ev_report_template'
    _description = 'New EV Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info("New EV Report: _get_report_values called.")
        
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        service_request_type_fixed = data.get('service_request_type_fixed') # Should be 'new_ev'

        _logger.info(f"New EV Report Parameters: From Date: {from_date}, To Date: {to_date}, Service Request Type: {service_request_type_fixed}")

        # Convert string dates to date objects if they are strings
        if isinstance(from_date, str):
            from_date = fields.Date.from_string(from_date)
        if isinstance(to_date, str):
            to_date = fields.Date.from_string(to_date)
        
        _logger.info(f"Converted Dates: From Date: {from_date} (type: {type(from_date)}), To Date: {to_date} (type: {type(to_date)})")

        # Search for the 'Issuance of New EV' service request configuration
        service_request_config = self.env['service.request.config'].search([
            ('name', '=', 'Issuance of New EV')
        ], limit=1)
        service_request_config_id = service_request_config.id
        
        _logger.info(f"Service Request Config Found: {service_request_config.name} (ID: {service_request_config_id})")

        # Prepare default return data in case of no config or no enquiries
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'new.ev.report.wizard',
            'docs': [], # Initialize with empty docs
            'data': data,
            'from_date': from_date,
            'to_date': to_date,
            'service_request_type_fixed_label': 'Issuance of New EV', # Always pass the label
        }

        if not service_request_config_id:
            _logger.error("New EV Report: 'Issuance of New EV' Service Request Config not found! Returning empty report.")
            return base_return_data

        service_enquiry_model = self.env['service.enquiry']

        # Construct the domain including date filtering and the specific service request config
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('create_date', '>=', from_date),
            ('create_date', '<=', to_date),
        ]
        _logger.info(f"Searching service.enquiry with domain: {enquiry_domain}")
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        _logger.info(f"Number of relevant enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            _logger.warning("New EV Report: No relevant service enquiries found for the given criteria. Returning empty report.")
            return base_return_data

        # Get unique employee IDs from the relevant enquiries
        # Assuming 'employee_id' field exists on 'service.enquiry'
        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)
        _logger.info(f"Number of employees found for New EV Report: {len(employees)}")
        
        # Log employee names for verification
        for emp in employees:
            _logger.info(f"New EV Employee: {emp.name}, IQAMA: {emp.iqama_no}") # Add more fields as needed for debugging

        report_data = [{
            'employees': employees,
            'service_request_type_fixed_label': 'Issuance of New EV',
            # You can add other derived data here if needed
        }]

        base_return_data['docs'] = report_data 
        _logger.info("New EV Report: Data prepared successfully. Returning report values.")
        return base_return_data