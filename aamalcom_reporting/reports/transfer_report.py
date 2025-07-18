from odoo import models, api, fields
from datetime import datetime, time

class TransferReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.transfer_report_template'
    _description = 'Transfer Request Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        transfer_type = data.get('transfer_type')
        service_request_type_fixed = data.get('service_request_type_fixed')

        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_str

        service_request_config = self.env['service.request.config'].search([
            ('name', '=', 'Transfer Request Initiation')
        ], limit=1)
        
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'transfer.report.wizard',
            'docs': [],
            'data': data,
            'transfer_type': transfer_type,
            'service_request_type_fixed': service_request_type_fixed,
            'transfer_type_label': dict(self.env['service.enquiry']._fields['transfer_type'].selection).get(transfer_type, transfer_type),
            'service_request_type_fixed_label': 'Transfer Request Initiation',
            'from_date': from_date_obj,
            'to_date': to_date_obj,
        }

        if not service_request_config:
            return base_return_data

        service_request_config_id = service_request_config.id

        service_enquiry_model = self.env['service.enquiry']

        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('transfer_type', '=', transfer_type),
        ]

        if from_date_obj:
            enquiry_domain.append(('processed_date', '>=', from_date_obj))
        if to_date_obj:
            enquiry_domain.append(('processed_date', '<=', to_date_obj))

        if service_request_type_fixed == 'transfer_req':
            enquiry_domain.append(('state', '=', 'done'))

        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        
        if not relevant_enquiries:
            return base_return_data

        report_lines = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            if employee:
                report_lines.append({
                    'employee_record': employee, # Keep employee record reference if needed
                    'employee_iqama_no': employee.iqama_no or '',
                    'employee_name': employee.name or '',
                    'employee_doj':employee.doj or '',
                    'employee_sponsor_name': employee.sponsor_id.name if employee.sponsor_id else '',
                    'employee_client_name': employee.client_parent_id.name if employee.client_parent_id else '', # Assuming client_parent_id for client
                    'employee_passport_id': employee.passport_id or '',
                    'employee_identification_id': employee.identification_id or '', # For Border No
                    'enquiry_transfer_type_label': dict(enquiry._fields['transfer_type'].selection).get(enquiry.transfer_type, enquiry.transfer_type) or '',
                    'enquiry_processed_date': enquiry.processed_date, # This is the key field
                })
        
        base_return_data['docs'] = [{
            'report_lines': report_lines, # Changed key to 'report_lines' for clarity in template
            'transfer_type_label': dict(service_enquiry_model._fields['transfer_type'].selection).get(transfer_type, transfer_type),
            'service_request_type_fixed_label': 'Transfer Request Initiation',
        }]
        
        return base_return_data