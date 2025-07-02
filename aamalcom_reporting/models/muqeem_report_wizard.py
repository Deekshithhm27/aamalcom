# models/muqeem_report_wizard.py

from odoo import models, fields, api, _

class MuqeemReportWizard(models.TransientModel):
    _name = 'muqeem.report.wizard'
    _description = 'Muqeem Report Wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    service_request = fields.Selection([
        ('hr_card','Issuance for HR card'),
        ('iqama_no_generation','Iqama Card Generation'),
        ('iqama_card_req','New Physical Iqama Card Request'),
        ('iqama_renewal','Iqama Renewal'),
        ('final_exit_issuance','Final exit Issuance'),
        ], string="Service Requests", required=True)
    
    # NEW FIELD ADDED: service_request_type
    service_request_type = fields.Selection([
        ('lt_request','Local Transfer'),
        ('ev_request','Employment Visa'),
        ('twv_request','Temporary Work Visa')
    ], string="Service Request Type", required=False) # Changed to required=False as it's an additional filter

    def print_muqeem_report(self):
        """
        Action to print the Muqeem report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request': self.service_request,
            'service_request_type': self.service_request_type, # Pass the new service_request_type
        }
        return self.env.ref('aamalcom_reporting.action_muqeem_report_pdf').report_action(self, data=data)