from odoo import models, api, fields
from datetime import datetime, time

class NewEvReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.new_ev_report_template'
    _description = 'New EV Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_type_fixed = data.get('service_request_type_fixed')

        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_str
        
        from_datetime = datetime.combine(from_date_obj, time.min) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, time.max) if to_date_obj else False

        service_request_config = self.env['service.request.config'].search([
            ('name', '=', 'Issuance of New EV')
        ], limit=1)
        
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'new.ev.report.wizard',
            'docs': [],
            'data': data,
            'from_date': from_date_obj,
            'to_date': to_date_obj,     
            'service_request_type_fixed_label': 'Issuance of New EV',
        }

        if not service_request_config:
            return base_return_data

        service_request_config_id = service_request_config.id

        service_enquiry_model = self.env['service.enquiry']

        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
        ]
        
        if from_date_obj:
            enquiry_domain.append(('processed_date', '>=', from_date_obj))
        if to_date_obj:
            enquiry_domain.append(('processed_date', '<=', to_date_obj))

        if service_request_type_fixed == 'new_ev':
            enquiry_domain.append(('state', '=', 'done'))
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)

        if not relevant_enquiries:
            return base_return_data

        report_lines = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            if employee:
                report_lines.append({
                    'employee_record': employee,
                    'employee_name': employee.name,
                    'employee_iqama_no': employee.iqama_no,
                    'employee_passport_id': employee.passport_id,
                    'employee_country_name': employee.country_id.name,
                    'employee_job_title': employee.job_title,
                    'employee_religion': employee.religion,
                    'employee_sponsor_name': employee.sponsor_id.name if employee.sponsor_id else '',
                    'employee_client_name': employee.client_parent_id.name if employee.client_parent_id else '',
                    'enquiry_name':enquiry.name,
                    'enquiry_visa_no': enquiry.emp_visa_id,
                    'enquiry_iqama_no': enquiry.iqama_no,
                    'enquiry_processed_date': enquiry.processed_date,
                    'enquiry_identification_id': enquiry.identification_id,
                })
        
        base_return_data['docs'] = [{'employees': report_lines}]

        return base_return_data