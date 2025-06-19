# models/muqeem_report_wizard.py

from odoo import models, fields, api, _

class MuqeemReportWizard(models.TransientModel):
    _name = 'muqeem.report.wizard'
    _description = 'Muqeem Report Wizard'

    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    service_request = fields.Selection([
        ('new_ev','Issuance of New EV'),
        ('sec','SEC Letter'),
        ('hr_card','Issuance for HR card'),
        ('transfer_req','Transfer Request Initiation'),
        ('ins_class_upgrade','Medical health insurance Class Upgrade'),
        ('iqama_no_generation','Iqama Card Generation'),
        ('iqama_card_req','New Physical Iqama Card Request'),
        ('qiwa','Qiwa Contract'),
        ('gosi','GOSI Update'),
        ('iqama_renewal','Iqama Renewal'),
        ('prof_change_qiwa','Profession change Request In qiwa'),
        ('salary_certificate','Salary certificate'),
        ('bank_letter','Bank letter'),
        ('vehicle_lease','Letter for Vehicle Lease'),
        ('apartment_lease','Letter for Apartment Lease'),
        ('employment_contract','Employment contract'),
        ('cultural_letter','Cultural Letter/Bonafide Letter'),
        ('emp_secondment_or_cub_contra_ltr','Employee secondment / Subcontract letter'),
        ('car_loan','Car Loan Letter'),
        ('rental_agreement','Rental Agreement Letter'),
        ('exception_letter','Exception Letter'),
        ('attestation_waiver_letter','Attestation Waiver Letter'),
        ('embassy_letter','Embassy Letters- as Per Respective Embassy requirement'),
        ('istiqdam_letter','Istiqdam Letter'),
        ('sce_letter','SCE Letter'),
        ('bilingual_salary_certificate','Bilingual Salary Certificate'),
        ('contract_letter','Contract Letter'),
        ('bank_account_opening_letter','Bank account Opening Letter'),
        ('bank_limit_upgrading_letter','Bank Limit upgrading Letter'),
        ('final_exit_issuance','Final exit Issuance'),
        ('dependent_transfer_query','Dependent Transfer Query'),
        ('soa','Statement of account till date')
    ], string="Service Requests", required=True)

    def print_muqeem_report(self):
        """
        Action to print the Muqeem report.
        """
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'service_request': self.service_request, # Pass the new service_request field
        }
        # The 'action_muqeem_report_pdf' will be defined in XML later
        return self.env.ref('aamalcom_reporting.action_muqeem_report_pdf').report_action(self, data=data)