from odoo import models, fields, api

class ServiceEnquiry(models.Model):
    _inherit = 'service.request.config'

    service_request = fields.Selection(
    selection_add=[
        ('bank_loan','Bank Loan Letter'),
        ('vehicle_lease','Letter for Vehicle Lease'),
        ('apartment_lease','Letter for Apartment Lease'),
        ('istiqdam_letter','Istiqdam Letter'),
        ('cultural_letter','Cultural Letter/Bonafide Letter'),
        ('emp_secondment_or_cub_contra_ltr','Employee secondment / Subcontract letter'),
        ('bank_letter','Bank letter'),
        ('car_loan','Car Loan Letter'),
        ('rental_agreement','Rental Agreement Letter'),
        ('exception_letter','Exception Letter'),
        ('attestation_waiver_letter','Attestation Waiver Letter'),
        ('embassy_letter','Embassy Letters- as Per Respective Embassy requirement'),
        ('sce_letter','SCE Letter'),
        ('bilingual_salary_certificate','Bilingual Salary Certificate'),
        ('contract_letter','Contract Letter'),
        ('bank_account_opening_letter','Bank account Opening Letter'),
        ('bank_limit_upgrading_letter','Bank Limit upgrading Letter'),('employment_contract','Employment contract'),
    ],
    string="Service Requests",
    store=True,
    copy=False,
    ondelete={
        'bank_loan': 'cascade',
        'vehicle_lease': 'cascade',
        'apartment_lease': 'cascade',
        'istiqdam_letter': 'cascade',
        'cultural_letter': 'cascade',
        'emp_secondment_or_cub_contra_ltr': 'cascade',
        'bank_letter': 'cascade',
        'car_loan': 'cascade',
        'rental_agreement': 'cascade',
        'exception_letter': 'cascade',
        'attestation_waiver_letter': 'cascade',
        'embassy_letter': 'cascade',
        'sce_letter': 'cascade',
        'bilingual_salary_certificate': 'cascade',
        'contract_letter': 'cascade',
        'bank_account_opening_letter': 'cascade',
        'bank_limit_upgrading_letter': 'cascade',
        'employment_contract':'cascade',
    }
    )
