# aamalcom_reporting/reports/muqeem_repoert.py

import logging
from odoo import models, api, fields
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class MuqeemReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.muqeem_report_template'
    _description = 'Muqeem Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info("Muqeem Report: _get_report_values called.")
        
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_key = data.get('service_request')
        # service_request_type_key is no longer needed

        _logger.info(f"Muqeem Report Parameters: From Date: {from_date_str}, To Date: {to_date_str}, Service Request Key: {service_request_key}")

        # Convert string dates to datetime objects for accurate range filtering
        from_date_obj = fields.Date.from_string(from_date_str) if from_date_str else False
        to_date_obj = fields.Date.from_string(to_date_str) if to_date_str else False

        from_datetime = datetime.combine(from_date_obj, datetime.min.time()) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, datetime.max.time()) if to_date_obj else False

        _logger.info(f"Converted Datetimes for Domain: From Datetime: {from_datetime}, To Datetime: {to_datetime}")

        # Get human-readable labels for display and search
        service_request_label = dict(self.env['muqeem.report.wizard']._fields['service_request'].selection).get(service_request_key, service_request_key)
        
        _logger.info(f"Service Request Label: {service_request_label}")

        # Search for service.request.config by its 'name'
        service_request_config_record = self.env['service.request.config'].search([
            ('name', '=', service_request_label)
        ], limit=1)
        
        service_request_config_id = service_request_config_record.id if service_request_config_record else False
        _logger.info(f"Service Request Config Found: {service_request_config_record.name} (ID: {service_request_config_id})")

        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'muqeem.report.wizard',
            'docs': [],
            'data': data, # Original data from wizard
            'from_date': from_date_obj, # Pass date objects for template formatting
            'to_date': to_date_obj,
            'service_request_selected': service_request_key,
            'service_request_label': service_request_label,
            # service_request_type_selected and service_request_type_label are removed
        }

        if not service_request_config_record:
            _logger.error(f"Muqeem Report: Service Request Config with name '{service_request_label}' not found! Returning empty report.")
            return base_return_data

        service_enquiry_model = self.env['service.enquiry']
        
        # Construct the domain for service.enquiry
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('create_date', '>=', from_datetime),
            ('create_date', '<=', to_datetime),
            ('state', '=', 'done'),  # ADDED: Filter by state = 'done'
        ]
        
        _logger.info(f"Searching service.enquiry with domain: {enquiry_domain}")
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        _logger.info(f"Number of relevant enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            _logger.warning("Muqeem Report: No relevant service enquiries found for the given criteria. Returning empty report.")
            return base_return_data

        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)
        _logger.info(f"Number of employees found: {len(employees)}")
        
        for emp in employees:
            _logger.info(f"Employee: {emp.name}, Iqama: {emp.iqama_no}, Client: {emp.client_parent_id.name if emp.client_parent_id else 'N/A'}")

        report_data = [{
            'employees': employees,
            'service_request_label': service_request_label,
            # service_request_type_label is removed
        }]
        
        base_return_data['docs'] = report_data
        _logger.info("Muqeem Report: Data prepared successfully. Returning report values.")
        return base_return_data