# aamalcom_reporting/models/qiwa_contract_report_wizard.py

from odoo import models, fields, api, _

class QiwaContractReportWizard(models.TransientModel):
    _name = 'qiwa.contract.report.wizard'
    _description = 'Qiwa Contract Report Wizard'

    # Fixed service request type for "Qiwa Contract"
    service_request_type_fixed = fields.Selection([
        ('qiwa', 'Qiwa Contract')
    ], string="Service Request Name", default='qiwa', readonly=True, store=True)

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)

    def print_qiwa_contract_report(self):
        """
        Action to print the Qiwa Contract Report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        # Reference the new report action defined in qiwa_contract_report_action.xml
        return self.env.ref('aamalcom_reporting.action_qiwa_contract_report_pdf').report_action(self, data=data)

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
        Action to print the Qiwa Contract Report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        # Reference the new report action defined in qiwa_contract_report_action.xml
        return self.env.ref('aamalcom_reporting.action_qiwa_report_pdf').report_action(self, data=data)