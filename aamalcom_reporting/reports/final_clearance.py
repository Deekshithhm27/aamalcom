# aamalcom_reporting/reports/final_clearance_report.py

from odoo import models, api, fields
from datetime import datetime, time

class FinalClearanceReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.final_clearance_report_template'
    _description = 'Final Clearance Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_type_fixed = data.get('service_request_type_fixed') # Should be 'final_clearance'
        final_clearance_type_selected = data.get('final_clearance_type') # Selected type from wizard

        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_str

        from_datetime = datetime.combine(from_date_obj, time.min) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, time.max) if to_date_obj else False

        final_clearance_type_label = dict(self.env['final.clearance.report.wizard']._fields['final_clearance_type'].selection).get(final_clearance_type_selected, final_clearance_type_selected)

        # --- Debugging Prints ---
        print(f"\n--- Final Clearance Report Generation Debug ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
        print(f"1. Wizard Inputs: From Date='{from_date_str}', To Date='{to_date_str}', Service Request Type='{service_request_type_fixed}', Final Clearance Type='{final_clearance_type_selected}'")
        print(f"2. Converted Datetimes: from_datetime='{from_datetime}', to_datetime='{to_datetime}'")
        # --- End Debugging Prints ---

        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'final.clearance.report.wizard',
            'docs': [],
            'data': data,
            'service_request_type_fixed': service_request_type_fixed,
            'service_request_type_fixed_label': 'Final Clearance',
            'final_clearance_type_selected': final_clearance_type_selected,
            'final_clearance_type_label': final_clearance_type_label,
            'from_date': from_date_obj,
            'to_date': to_date_obj,
        }

        service_request_config = self.env['service.request.config'].search([
            ('service_request', '=', 'final_clearance')
        ], limit=1)

        if not service_request_config:
            print("WARNING: 'Final Clearance' service.request.config NOT FOUND! Returning empty report.")
            return base_return_data

        print(f"3. Found Service Request Config 'Final Clearance': ID={service_request_config.id}, Name='{service_request_config.name}'")

        service_enquiry_model = self.env['service.enquiry']

        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config.id),
            ('service_request', '=', 'final_clearance'),
        ]

        if from_datetime:
            enquiry_domain.append(('create_date', '>=', from_datetime))
        if to_datetime:
            enquiry_domain.append(('create_date', '<=', to_datetime))

        # IMPORTANT: Adjust state filter based on your service.enquiry states
        # The 'state' field values will vary depending on your 'visa_process' module's implementation.
        # You need to confirm the actual states used for 'final_clearance_local_transfer' and 'final_clearance_final_exit'.
        # For example, if 'final_exit_issuance' is a state for final exits and 'completed_transfer' for local transfers:
        if final_clearance_type_selected == 'final_clearance_final_exit':
            enquiry_domain.append(('state', '=', 'final_exit_issuance')) # Example state for final exit
        elif final_clearance_type_selected == 'final_clearance_local_transfer':
            enquiry_domain.append(('state', '=', 'done')) # Example state for local transfer completion

        print(f"4. Final service.enquiry search domain: {enquiry_domain}")
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)

        print(f"5. Number of relevant service enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            print("No relevant enquiries found based on the domain. Returning empty report.")
            return base_return_data

        report_lines = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            if employee:
                report_lines.append({
                    'emp_record': employee,
                    'enquiry_record': enquiry,
                    'iqama_no': enquiry.iqama_no,
                    'name': employee.name,
                    'sponsor_name': enquiry.sponsor_id.name,
                    'client_name': employee.client_parent_id.name, # Assuming client is client_parent_id on employee
                    'passport_no': enquiry.passport_no,
                    'border_no': enquiry.identification_id,
                    'processed_date': enquiry.processed_date,
                    'final_clearance_type_label': final_clearance_type_label,

                    # --- ADDED FOR MUQEEM-LIKE COLUMNS ---
                    'gender_label': dict(employee._fields['gender'].selection).get(employee.gender) if employee.gender else '',
                    'country_name': employee.country_id.name,
                    'job_title': employee.job_title,
                    'iqama_issue_date': enquiry.processed_date, # Assuming processed_date is used for this
                    'iqama_expiry_date': enquiry.processed_date, # Assuming processed_date is used for this, or find correct field
                    'doj': employee.doj,
                    'birthday': employee.birthday,
                    'active_status': employee.active,
                    'processed_date': enquiry.processed_date,
                     # Assuming this is the field for last working date
                    # --- END ADDED ---
                })

        base_return_data['docs'] = [{'employees': report_lines}]

        print(f"6. Report will attempt to display data for {len(report_lines)} report lines.")
        print(f"--- Debugging Complete ---")

        return base_return_data