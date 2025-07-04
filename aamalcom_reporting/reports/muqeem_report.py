from odoo import models, api, fields


class MuqeemReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.muqeem_report_template'
    _description = 'Muqeem Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        service_request_selected = data.get('service_request') 
        service_request_config_record = self.env['service.request.config'].search([
            ('service_request', '=', service_request_selected)
        ], limit=1)
        if not service_request_config_record:
            return {
                'doc_ids': docids,
                'doc_model': 'muqeem.report.wizard',
                'docs': [], 
                'data': data,
                'service_request_selected': service_request_selected,
                'service_request_label': dict(self.env['muqeem.report.wizard']._fields['service_request'].selection).get(service_request_selected, service_request_selected),
            }
        employee_model = self.env['hr.employee']
        service_enquiry_model = self.env['service.enquiry'] 
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_record.id),
        ]
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)
        

        if not relevant_enquiries:
            return {
                'doc_ids': docids,
                'doc_model': 'muqeem.report.wizard',
                'docs': [], # Return empty docs if no employees found
                'data': data,
                'service_request_selected': service_request_selected,
                'service_request_label': dict(self.env['muqeem.report.wizard']._fields['service_request'].selection).get(service_request_selected, service_request_selected),
            }

        
        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = employee_model.browse(employee_ids)
        service_request_label = dict(self.env['muqeem.report.wizard']._fields['service_request'].selection).get(service_request_selected, service_request_selected)
        report_data = [{
            'employees': employees,
            'service_request_label': service_request_label,
        }]
        return {
            'doc_ids': docids,
            'doc_model': 'muqeem.report.wizard',
            'docs': report_data,
            'data': data,
            'service_request_selected': service_request_selected,
        }