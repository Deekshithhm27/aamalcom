# aamalcom_reporting/models/qiwa_report_wizard.py

from odoo import models, fields, api, _

class QiwaReportWizard(models.TransientModel):
    _name = 'qiwa.report.wizard'
    _description = 'QIWA Report Wizard'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    
    # Fixed service request type for "Qiwa Contract"
    service_request_type_fixed = fields.Selection([
        ('qiwa','Qiwa Contract')
    ], string="Service Request Name", default='qiwa', readonly=True, store=True)

    def print_qiwa_report(self):
        """
        Action to print the QIWA Report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        # Reference the new report action defined in qiwa_report_action.xml
        return self.env.ref('aamalcom_reporting.action_qiwa_report_pdf').report_action(self, data=data)