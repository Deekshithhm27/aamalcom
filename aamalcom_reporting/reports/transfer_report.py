from odoo import models, api, fields

class TransferReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.transfer_report_template'
    _description = 'Transfer Request Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        transfer_type = data.get('transfer_type')
        service_request_config_id = self.env['service.request.config'].search([
            ('name', '=', 'Transfer Request Initiation') # Search by name
        ], limit=1).id

        if not service_request_config_id:
            _logger.error("Transfer Report: 'Transfer Request Initiation' Service Request Config not found!")
            return {
                'doc_ids': docids,
                'doc_model': 'transfer.report.wizard',
                'docs': [],
                'data': data,
                'transfer_type': transfer_type,
                'service_request_type_fixed': 'transfer_req',
                'transfer_type_label': dict(self.env['service.enquiry']._fields['transfer_type'].selection).get(transfer_type, transfer_type),
                'service_request_type_fixed_label': 'Transfer Request Initiation',
            }

        

        employee_model = self.env['hr.employee']
        service_enquiry_model = self.env['service.enquiry'] 
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_id), # Corrected field and value
            ('transfer_type', '=', transfer_type),
        ]
        
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        

        if not relevant_enquiries:
            _logger.warning("Transfer Report: No relevant service enquiries found for the given criteria.")
            # Return empty docs if no employees found after enquiry search
            return {
                'doc_ids': docids,
                'doc_model': 'transfer.report.wizard',
                'docs': [],
                'data': data,
                'transfer_type': transfer_type,
                'service_request_type_fixed': 'transfer_req', # Still pass for wizard label
                'transfer_type_label': dict(service_enquiry_model._fields['transfer_type'].selection).get(transfer_type, transfer_type),
                'service_request_type_fixed_label': 'Transfer Request Initiation',
            }

        # Get unique employee IDs from the relevant enquiries
        employee_ids = relevant_enquiries.mapped('employee_id').ids
        

        employees = employee_model.browse(employee_ids)

        transfer_type_label = dict(service_enquiry_model._fields['transfer_type'].selection).get(transfer_type, transfer_type)
        # Service Request Type label is fixed as per requirement
        service_request_type_fixed_label = 'Transfer Request Initiation'
        
        report_data = [{
            'employees': employees,
            'transfer_type_label': transfer_type_label,
            'service_request_type_fixed_label': service_request_type_fixed_label,
        }]


        return {
            'doc_ids': docids,
            'doc_model': 'transfer.report.wizard',
            'docs': report_data,
            'data': data,
            'transfer_type': transfer_type,
            'service_request_type_fixed': 'transfer_req', # Still pass for wizard label
        }