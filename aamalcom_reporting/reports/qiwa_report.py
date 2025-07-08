# aamalcom_reporting/reports/qiwa_report.py
from odoo import models, api, fields
from datetime import datetime, time

class QiwaReport(models.AbstractModel):
    # CORRECTED: This name must match report_name/report_file in qiwa_action.xml
    _name = 'report.aamalcom_reporting.qiwa_report_template'
    _description = 'Qiwa Report PDF'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')
        service_request_type_fixed = data.get('service_request_type_fixed') # This should be 'qiwa' from the wizard

        # Convert string dates (from wizard) to date objects
        from_date_obj = fields.Date.from_string(from_date_str) if isinstance(from_date_str, str) else from_date_str
        to_date_obj = fields.Date.from_string(to_date_str) if isinstance(to_date_str, str) else to_date_str

        # Convert date objects to datetime objects for accurate range filtering on 'create_date'
        from_datetime = datetime.combine(from_date_obj, time.min) if from_date_obj else False
        to_datetime = datetime.combine(to_date_obj, time.max) if to_date_obj else False

        # --- Debugging Prints ---
        print(f"\n--- Qiwa Report Generation Debug ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
        print(f"1. Wizard Inputs: From Date='{from_date_str}', To Date='{to_date_str}', Service Request Type='{service_request_type_fixed}'")
        print(f"2. Converted Datetimes: from_datetime='{from_datetime}', to_datetime='{to_datetime}'")
        # --- End Debugging Prints ---

        # Prepare base return data (important even if no records are found)
        base_return_data = {
            'doc_ids': docids,
            'doc_model': 'qiwa.report.wizard',
            'docs': [], # Initialize with empty docs
            'data': data,
            'service_request_type_fixed': service_request_type_fixed,
            'service_request_type_fixed_label': 'Qiwa Contract', # This label is for display in the report
            'from_date': from_date_obj, # Pass original date objects for display in the report template
            'to_date': to_date_obj,     # Pass original date objects for display in the report template
        }

        service_enquiry_model = self.env['service.enquiry']

        enquiry_domain = []

        # PRIMARY FILTER: Filter by the 'service_request' field directly on service.enquiry
        # The technical value for 'Qiwa Contract' is 'qiwa' based on your model definition.
        if service_request_type_fixed == 'qiwa':
            enquiry_domain.append(('service_request', '=', 'qiwa'))
        else:
            # If the wizard allows other 'service_request_type_fixed' values,
            # you'd handle them here or return empty if 'qiwa' is expected.
            print(f"WARNING: service_request_type_fixed is not 'qiwa' (it's '{service_request_type_fixed}'). Report will be empty for this reason.")
            return base_return_data

        # Add date range filters if dates are provided
        if from_datetime:
            enquiry_domain.append(('create_date', '>=', from_datetime))
        if to_datetime:
            enquiry_domain.append(('create_date', '<=', to_datetime))

        # Re-add the state filter, confirmed to be 'done' for 'Completed'
        enquiry_domain.append(('state', '=', 'done'))

        # --- Debugging Prints ---
        print(f"3. Final service.enquiry search domain: {enquiry_domain}")
        # --- End Debugging Prints ---

        # Perform the search for relevant service enquiries
        relevant_enquiries = service_enquiry_model.sudo().search(enquiry_domain)

        # --- Debugging Prints ---
        print(f"4. Number of relevant service enquiries found: {len(relevant_enquiries)}")
        # --- End Debugging Prints ---

        # If no relevant enquiries are found, return empty report
        if not relevant_enquiries:
            print("No relevant enquiries found based on the domain. Returning empty report.")
            return base_return_data

        # Extract unique employee IDs from the found enquiries and browse them
        employee_ids = relevant_enquiries.mapped('employee_id').ids
        employees = self.env['hr.employee'].browse(employee_ids)

        # Prepare the report data to be passed to the template
        report_data = [{
            'employees': employees,
            'service_request_type_fixed_label': 'Qiwa Contract', # Still hardcoded for the label
        }]

        # Set the 'docs' key in base_return_data with the actual report data
        base_return_data['docs'] = report_data

        # --- Debugging Prints ---
        print(f"5. Report will attempt to display data for {len(employees)} employees.")
        print(f"--- Debugging Complete ---")
        # --- End Debugging Prints ---

        return base_return_data