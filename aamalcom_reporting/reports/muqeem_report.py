# muqeem/reports/muqeem_reports.py
from odoo import models, api, fields
from datetime import datetime, time

class MuqeemReport(models.AbstractModel):
    _name = 'report.aamalcom_reporting.muqeem_report_template'
    _description = 'Muqeem Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Extract data from the wizard
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_selected = data.get('service_request')

        # Convert date strings to datetime objects for accurate filtering
        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_obj

        from_datetime = datetime.combine(from_date_obj, time.min) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, time.max) if to_date_obj else False

        # Debugging prints
        print(f"\n--- Muqeem Report Generation Debug ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
        print(f"1. Wizard Inputs: From Date='{from_date_str}', To Date='{to_date_str}', Service Request='{service_request_selected}'")
        print(f"2. Converted Datetimes: from_datetime='{from_datetime}', to_datetime='{to_datetime}'")

        # Get the label for the selected service request from the wizard's selection field
        service_request_label = dict(self.env['muqeem.report.wizard']._fields['service_request'].selection).get(service_request_selected, service_request_selected)

        # Base return data structure
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'muqeem.report.wizard',
            'docs': [],  # Initialize with empty docs, will be populated with our prepared list
            'data': data, # Pass original data for general use (e.g., displaying from/to dates)
            'service_request_selected': service_request_selected,
            'service_request_label': service_request_label,
            'from_date': from_date_obj, # Pass original date objects for display in the report template
            'to_date': to_date_obj,     # Pass original date objects for display in the report template
        }

        # Search for the service.request.config record based on the selected service_request
        service_request_config_record = self.env['service.request.config'].search([
            ('service_request', '=', service_request_selected)
        ], limit=1)

        if not service_request_config_record:
            print(f"WARNING: service.request.config not found for service_request='{service_request_selected}'. Returning empty report.")
            return base_return_data # Return empty if config not found

        print(f"3. Found Service Request Config '{service_request_config_record.name}': ID={service_request_config_record.id}")

        service_enquiry_model = self.env['service.enquiry']

        # Build the domain for service.enquiry
        enquiry_domain = [
            ('service_request_config_id', '=', service_request_config_record.id),
        ]

        # ADD DATE FILTERS HERE
        if from_datetime:
            enquiry_domain.append(('create_date', '>=', from_datetime)) # Use create_date or processed_date
        if to_datetime:
            enquiry_domain.append(('create_date', '<=', to_datetime))   # Use create_date or processed_date

        # Add a state filter if you want to limit to 'completed' or 'done' enquiries
        # enquiry_domain.append(('state', '=', 'done'))

        print(f"4. Final service.enquiry search domain: {enquiry_domain}")

        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)

        print(f"5. Number of relevant service enquiries found: {len(relevant_enquiries)}")

        if not relevant_enquiries:
            print("No relevant enquiries found based on the domain. Returning empty report.")
            return base_return_data

        # --- REVISED MAJOR CHANGE: Prepare data for the template ---
        # We will create a list where each item is a dictionary containing
        # both the employee record and the associated enquiry record,
        # plus any specific fields directly from the enquiry for easy access.
        report_data_list = []
        for enquiry in relevant_enquiries:
            employee = enquiry.employee_id
            if employee: # Ensure employee exists
                report_data_list.append({
                    'emp_record': employee,             # The hr.employee record (for standard fields)
                    'enquiry_record': enquiry,          # The service.enquiry record (for fields like processed_date)
                    'iqama_no': enquiry.iqama_no,       # Direct from enquiry or employee (consistent access)
                    'passport_id': enquiry.passport_no, # Use passport_no from enquiry if available/accurate
                    'sponsor_name': enquiry.sponsor_id.name, # From enquiry or employee
                    'req_completion_date': enquiry.processed_date,
                    'iqama_issue_date':enquiry.iqama_issue_date,
                    'iqama_expiry_date':enquiry.iqama_expiry_date,
                    'doj': employee.doj,                # From employee
                    'birthday': employee.birthday,      # From employee
                    'client_parent_id_name': employee.client_parent_id.name, # From employee
                    'active_status': employee.active, # From employee
                    'gender_label': dict(employee._fields['gender'].selection).get(employee.gender) if employee.gender else '',
                    'country_name': employee.country_id.name,
                    'job_title': employee.job_title,
                    # Assuming this is 'date_end' from hr.employee
                    # Add any other fields you need directly here for easy template access
                })
        # --- END REVISED MAJOR CHANGE ---

        # Structure the 'docs' to explicitly use 'employees' key as your XML expects
        base_return_data['docs'] = [{'employees': report_data_list}]

        print(f"6. Report will attempt to display data for {len(report_data_list)} employees/enquiries.")
        print(f"--- Debugging Complete ---")

        return base_return_data