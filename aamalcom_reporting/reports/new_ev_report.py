
import logging
from odoo import models, api, fields


class NewEvReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.new_ev_report_template'
    _description = 'New EV Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        service_request_type_fixed = data.get('service_request_type_fixed')

        if isinstance(from_date, str):
            from_date = fields.Date.from_string(from_date)
        if isinstance(to_date, str):
            to_date = fields.Date.from_string(to_date)
        
        service_request_config = self.env['service.request.config'].search([
            ('name', '=', 'Issuance of New EV')
        ], limit=1)
        service_request_config_id = service_request_config.id
        
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'new.ev.report.wizard',
            'docs': [],
            'data': data,
            'from_date': from_date,
            'to_date': to_date,
            'service_request_type_fixed_label': 'Issuance of New EV',
        }

        if not service_request_config_id:
            return base_return_data

        service_enquiry_model = self.env['service.enquiry']

        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('processed_date', '>=', from_date),
            ('processed_date', '<=', to_date),
        ]

        if service_request_type_fixed == 'new_ev':
            enquiry_domain.append(('state', '=', 'done'))
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)

        if not relevant_enquiries:
            return base_return_data

        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)
            
        report_data = [{
            'employees': employees,
            'service_request_type_fixed_label': 'Issuance of New EV',
        }]

        base_return_data['docs'] = report_data
        return base_return_data