import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class TransferReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.transfer_report_template'
    _description = 'Transfer Request Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        transfer_type = data.get('transfer_type')
        service_request_type_fixed = data.get('service_request_type_fixed') # Get this from data

        # Convert string dates to date objects if they are strings (important for comparison)
        if isinstance(from_date, str):
            from_date = fields.Date.from_string(from_date)
        if isinstance(to_date, str):
            to_date = fields.Date.from_string(to_date)

        service_request_config_id = self.env['service.request.config'].search([
            ('name', '=', 'Transfer Request Initiation')
        ], limit=1).id

        # Prepare default return data in case of no config or no enquiries
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'transfer.report.wizard',
            'docs': [], # Initialize with empty docs
            'data': data,
            'transfer_type': transfer_type,
            'service_request_type_fixed': service_request_type_fixed, # Pass this value
            'transfer_type_label': dict(self.env['service.enquiry']._fields['transfer_type'].selection).get(transfer_type, transfer_type),
            'service_request_type_fixed_label': 'Transfer Request Initiation', # This can be fetched dynamically too if needed
            'from_date': from_date, # Pass dates for display in the report
            'to_date': to_date,     # Pass dates for display in the report
        }

        if not service_request_config_id:
            _logger.error("Transfer Report: 'Transfer Request Initiation' Service Request Config not found!")
            return base_return_data # Return with empty docs

        service_enquiry_model = self.env['service.enquiry']

        # Construct the domain including date filtering and the new 'state' condition
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id),
            ('transfer_type', '=', transfer_type),
            ('create_date', '>=', from_date),
            ('create_date', '<=', to_date),
        ]

        # Add the 'state' condition specifically for 'transfer_req'
        if service_request_type_fixed == 'transfer_req':
            enquiry_domain.append(('state', '=', 'done'))
            _logger.info(f"Adding state='done' filter for transfer_req. Current domain: {enquiry_domain}")
        else:
            _logger.info(f"Service request type is not transfer_req. Not adding state filter. Current domain: {enquiry_domain}")


        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        
        if not relevant_enquiries:
            _logger.warning("Transfer Report: No relevant service enquiries found for the given criteria.")
            return base_return_data # Return with empty docs

        # Get unique employee IDs from the relevant enquiries
        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)

        transfer_type_label = dict(service_enquiry_model._fields['transfer_type'].selection).get(transfer_type, transfer_type)
        service_request_type_fixed_label = 'Transfer Request Initiation' # Still hardcoded, but can be dynamic if needed
        
        report_data = [{
            'employees': employees,
            'transfer_type_label': transfer_type_label,
            'service_request_type_fixed_label': service_request_type_fixed_label,
        }]

        # Include report_data in the final return, which contains the 'employees'
        base_return_data['docs'] = report_data 
        return base_return_data