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
        service_request_key = data.get('service_request_type_fixed') # This will be 'qiwa' from the wizard

        _logger.info(f"QIWA Report Parameters: From Date (str): {from_date_str}, To Date (str): {to_date_str}, Service Request Key: {service_request_key}")

        # Convert string dates to date objects
        from_date = fields.Date.from_string(from_date_str) if from_date_str else False
        to_date = fields.Date.from_string(to_date_str) if to_date_str else False

        # Convert date objects to datetime objects for accurate range filtering on 'create_date' (which is datetime)
        # Ensure to_datetime includes the entire day
        from_datetime = datetime.combine(from_date, datetime.min.time()) if from_date else False
        to_datetime = datetime.combine(to_date, datetime.max.time()) if to_date else False

        _logger.info(f"Converted Datetimes for Domain: From Datetime: {from_datetime}, To Datetime: {to_datetime}")

        # Get the human-readable label for the service request from the wizard's selection
        # This label MUST exactly match the 'Name' of your service.request.config record
        # It's 'Qiwa Contract' based on your wizard
        service_request_label = dict(self.env['qiwa.report.wizard']._fields['service_request_type_fixed'].selection).get(service_request_key, service_request_key)
        _logger.info(f"Service Request Label (to find config): {service_request_label}")

        # Search for service.request.config by its 'name'
        service_request_config_record = self.env['service.request.config'].search([
            ('name', '=', service_request_label) # This will be ('name', '=', 'Qiwa Contract')
        ], limit=1)
        
        service_request_config_id = service_request_config_record.id if service_request_config_record else False
        _logger.info(f"Service Request Config Found: {service_request_config_record.name if service_request_config_record else 'NOT FOUND'} (ID: {service_request_config_id})")

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
        ]
        
        # Add date filters if dates are provided
        if from_datetime:
            enquiry_domain.append(('create_date', '>=', from_datetime))
        if to_datetime:
            enquiry_domain.append(('create_date', '<=', to_datetime))

        # ADD THE NEW CONDITION HERE: if service_request_type is 'qiwa', also filter by state 'done'
        if service_request_key == 'qiwa':
            enquiry_domain.append(('state', '=', 'done'))
            _logger.info(f"Added state='done' filter for service_request_key='qiwa'.")
        else:
            _logger.info(f"No state='done' filter applied as service_request_key is not 'qiwa'.")
            
        _logger.info(f"Final service.enquiry search domain: {enquiry_domain}")
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        _logger.info(f"Number of relevant enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            _logger.warning("QIWA Report: No relevant service enquiries found for the given criteria. Returning empty report.")
            return base_return_data

        # --- Data preparation for the report ---
        # Instead of just employees, you likely need details from the service.enquiry record
        # along with employee details for each row.
        
        report_lines = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            
            # Ensure employee exists and is active (or whatever status is relevant for QIWA)
            if employee:
                report_lines.append({
                    'iqama_no': employee.iqama_no or '',
                    'name': employee.name or '',
                    'gender': dict(employee._fields['gender'].selection).get(employee.gender) if employee.gender else '',
                    'nationality': employee.country_id.name or '',
                    'occupation': employee.job_title or '',
                    'passport_id': employee.passport_id or '',
                    'sponsor_name': employee.sponsor_id.name or '',
                    'qiwa_contract_doc': employee.qiwa_contract_doc or '',
                    'qiwa_contract_sr_no': employee.qiwa_contract_sr_no or '',
                    # Use the 'request_completion_date' from the service.enquiry itself if that's the "Date of Issuance" for the QIWA report
                    'req_completion_date': enquiry.request_completion_date if hasattr(enquiry, 'request_completion_date') else '', 
                    'doj': employee.doj or '',
                    'birthday': employee.birthday or '',
                    'client_name': employee.client_parent_id.name or '',
                    'active': 'Yes' if employee.active else 'No', # Display 'Active' status
                    'date_end': employee.date_end or '', # Last Working Date
                    'enquiry_create_date': enquiry.create_date.strftime('%d-%m-%Y %H:%M:%S') if enquiry.create_date else '', # For debugging
                    'enquiry_state': dict(enquiry._fields['state'].selection).get(enquiry.state) if enquiry.state else '', # For debugging
                })
            else:
                _logger.warning(f"QIWA Report: Service Enquiry {enquiry.name} (ID: {enquiry.id}) has no linked employee.")


        # The 'docs' key should contain the list of dictionaries for the report lines
        base_return_data['docs'] = [{
            'report_lines': report_lines,
            'service_request_label': service_request_label,
            # Pass individual report metadata as needed
        }]
        
        _logger.info("QIWA Report: Data prepared successfully. Returning report values.")
        return base_return_data