# aamalcom_reporting/models/new_ev_report_wizard.py

from odoo import models, fields, api, _

class NewEvReportWizard(models.TransientModel):
    _name = 'new.ev.report.wizard'
    _description = 'New EV Report Wizard'

    # Fixed service request type for "Issuance of New EV"
    service_request_type_fixed = fields.Selection([
        ('new_ev', 'Issuance of New EV')
    ], string="Service Request Name", default='new_ev', readonly=True, store=True)

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)

    def print_new_ev_report(self):
        """
        Action to print the New EV Report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request_type_fixed': self.service_request_type_fixed,
        }
        # Reference the new report action defined in new_ev_report_action.xml
        return self.env.ref('aamalcom_reporting.action_new_ev_report_pdf').report_action(self, data=data)