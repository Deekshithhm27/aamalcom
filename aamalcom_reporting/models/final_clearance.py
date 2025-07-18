# aamalcom_reporting/models/final_clearance_report_wizard.py

from odoo import models, fields, api, _

class FinalClearanceReportWizard(models.TransientModel):
    _name = 'final.clearance.report.wizard'
    _description = 'Final Clearance Report Wizard'

    # Fixed service request type for "Final Clearance"
    service_request_type_fixed = fields.Selection([
        ('final_clearance', 'Final Clearance')
    ], string="Service Request Name", default='final_clearance', readonly=True, store=True)

    final_clearance_type = fields.Selection([
        ('final_clearance_local_transfer', 'Local Transfer'),
        ('final_clearance_final_exit', 'Final Exit')
    ], string="Final Clearance Type", required=True) # New field for specific clearance type

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)

    def print_final_clearance_report(self):
        """
        Action to print the Final Clearance Report.
        """
        self.ensure_one() # Ensures the method is called on a single record

        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
            'final_clearance_type': self.final_clearance_type, # Pass the selected clearance type
        }
        # Reference the new report action defined in final_clearance_action.xml
        return self.env.ref('aamalcom_reporting.action_final_clearance_report_pdf').report_action(self, data=data)