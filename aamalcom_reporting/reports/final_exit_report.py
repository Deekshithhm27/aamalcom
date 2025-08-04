# aamalcom_reporting/reports/final_exit_issuance_report.py

from odoo import models, api, fields
from datetime import datetime, time

class FinalExitIssuanceReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.final_exit_issuance_report_template'
    _description = 'Final Exit Issuance Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_type = data.get('service_request_type_fixed')
        is_inside_ksa = data.get('is_inside_ksa')
        is_outside_ksa = data.get('is_outside_ksa')

        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_str

        from_datetime = datetime.combine(from_date_obj, time.min) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, time.max) if to_date_obj else False

        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'final.exit.issuance.report.wizard',
            'docs': [],
            'data': data,
            'from_date': from_date_obj,
            'to_date': to_date_obj,
            'service_request_type': service_request_type,
            'report_filter_status': 'Inside KSA' if is_inside_ksa else ('Outside KSA' if is_outside_ksa else 'N/A')
        }

        # Find the correct service.request.config for 'final_exit_issuance'
        service_request_config = self.env['service.request.config'].search([
            ('service_request', '=', service_request_type)
        ], limit=1)

        if not service_request_config:
            print(f"WARNING: '{service_request_type}' service.request.config NOT FOUND! Returning empty report.")
            return base_return_data

        # Build the domain for searching service enquiries
        enquiry_domain = [
            ('service_request', '=', service_request_type),
            ('state', '=', 'done'),
        ]

        # Add date filtering if dates are provided
        if from_datetime:
            enquiry_domain.append(('create_date', '>=', from_datetime))
        if to_datetime:
            enquiry_domain.append(('create_date', '<=', to_datetime))
        
        # Add location filtering based on the boolean fields
        if is_inside_ksa:
            enquiry_domain.append(('is_inside_ksa', '=', True))
        if is_outside_ksa:
            enquiry_domain.append(('is_inside_ksa', '=', False))

        # Debug: Print the domain and search for records
        print(f"DEBUG: Searching with domain: {enquiry_domain}")
        
        # First, let's see how many total records exist for this service request
        total_records = self.env['service.enquiry'].sudo().search_count([
            ('service_request', '=', service_request_type)
        ])
        print(f"DEBUG: Total records with service_request='{service_request_type}': {total_records}")
        
        # Check how many are in 'done' state
        done_records = self.env['service.enquiry'].sudo().search_count([
            ('service_request', '=', service_request_type),
            ('state', '=', 'done')
        ])
        print(f"DEBUG: Records with service_request='{service_request_type}' and state='done': {done_records}")
        
        # Check date range if provided
        if from_datetime and to_datetime:
            date_range_records = self.env['service.enquiry'].sudo().search_count([
                ('service_request', '=', service_request_type),
                ('state', '=', 'done'),
                ('create_date', '>=', from_datetime),
                ('create_date', '<=', to_datetime)
            ])
            print(f"DEBUG: Records with date range {from_date_obj} to {to_date_obj}: {date_range_records}")

        relevant_enquiries = self.env['service.enquiry'].sudo().search(enquiry_domain)
        print(f"DEBUG: Final filtered records: {len(relevant_enquiries)}")

        report_lines = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            if employee:
                report_lines.append({
                    'iqama_no': enquiry.iqama_no or '',
                    'name': employee.name or '',
                    'sponsor_name': enquiry.sponsor_id.name if enquiry.sponsor_id else '',
                    'client_name': employee.client_parent_id.name if employee.client_parent_id else '',
                    'passport_no': enquiry.passport_no or '',
                    'border_no': enquiry.identification_id or '',
                    'processed_date': enquiry.processed_date,
                })

        base_return_data['docs'] = [{'employees': report_lines}]
        return base_return_data