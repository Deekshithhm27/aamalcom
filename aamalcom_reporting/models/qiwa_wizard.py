from odoo import models, fields, api, _

# Removed QiwaContractReportWizard class as per your request.
# Consolidating to qiwa.report.wizard
class QiwaReportWizard(models.TransientModel):
    _name = 'qiwa.report.wizard'
    _description = 'Qiwa Report Wizard'

    # Fixed service request type for "Qiwa Contract"
    service_request_type_fixed = fields.Selection([
        ('qiwa', 'Qiwa Contract')
    ], string="Service Request Name", default='qiwa', readonly=True, store=True)

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)

    def print_qiwa_report(self):
        """
        Action to print the Qiwa Report.
        """
        self.ensure_one() # Ensures the method is called on a single record

        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        # Reference the correct report action defined in reports/qiwa_action.xml
        return self.env.ref('aamalcom_reporting.action_qiwa_report_pdf').report_action(self, data=data)