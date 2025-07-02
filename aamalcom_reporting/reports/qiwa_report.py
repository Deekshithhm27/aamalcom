# aamalcom_reporting/reports/qiwa_report.py

import logging
from odoo import models, api, fields
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class QiwaReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.qiwa_report_template'
    _description = 'QIWA Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        _logger.info("QIWA Report: _get_report_values called.")
        
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_key = data.get('service_request_type_fixed') 

        _logger.info(f"QIWA Report Parameters: From Date (str): {from_date_str}, To Date (str): {to_date_str}, Service Request Key: {service_request_key}")

        # Convert string dates to date objects
        from_date = fields.Date.from_string(from_date_str) if from_date_str else False
        to_date = fields.Date.from_string(to_date_str) if to_date_str else False

        # Convert date objects to datetime objects for accurate range filtering
        from_datetime = datetime.combine(from_date, datetime.min.time()) if from_date else False
        to_datetime = datetime.combine(to_date, datetime.max.time()) if to_date else False

        _logger.info(f"Converted Datetimes for Domain: From Datetime: {from_datetime}, To Datetime: {to_datetime}")

        # Get the human-readable label for the service request from the wizard's selection
        # This label MUST exactly match the 'Name' of your service.request.config record
        service_request_label = dict(self.env['qiwa.report.wizard']._fields['service_request_type_fixed'].selection).get(service_request_key, service_request_key)
        _logger.info(f"Service Request Label: {service_request_label}")

        # Search for service.request.config by its 'name'
        service_request_config_record = self.env['service.request.config'].search([
            ('name', '=', service_request_label)
        ], limit=1)
        
        service_request_config_id = service_request_config_record.id if service_request_config_record else False
        _logger.info(f"Service Request Config Found: {service_request_config_record.name} (ID: {service_request_config_id})")

        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'qiwa.report.wizard',
            'docs': [],
            'data': data,
            'from_date': from_date,
            'to_date': to_date,
            'service_request_key': service_request_key,
            'service_request_label': service_request_label,
        }

        if not service_request_config_record:
            _logger.error(f"QIWA Report: Service Request Config with name '{service_request_label}' not found! Returning empty report.")
            return base_return_data

        service_enquiry_model = self.env['service.enquiry']
        
        # Construct the domain for service.enquiry
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('create_date', '>=', from_datetime),
            ('create_date', '<=', to_datetime),
        ]
        _logger.info(f"Searching service.enquiry with domain: {enquiry_domain}")
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        _logger.info(f"Number of relevant enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            _logger.warning("QIWA Report: No relevant service enquiries found for the given criteria. Returning empty report.")
            return base_return_data

        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)
        _logger.info(f"Number of employees found for QIWA Report: {len(employees)}")
        
        for emp in employees:
            _logger.info(f"Employee: {emp.name}, Iqama: {emp.iqama_no}, QIWA Contract: {emp.qiwa_contract_doc}, QIWA No: {emp.qiwa_contract_sr_no}, Req Completion Date: {emp.req_completion_date}")

        report_data = [{
            'employees': employees,
            'service_request_label': service_request_label,
        }]
        
        base_return_data['docs'] = report_data
        _logger.info("QIWA Report: Data prepared successfully. Returning report values.")
        return base_return_data