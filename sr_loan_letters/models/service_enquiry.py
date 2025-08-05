from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = "service.enquiry"

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
        ('bank_limit_upgrading_letter','Bank Limit upgrading Letter'),
        ('employment_contract','Employment contract'),
        ('salary_certificate','Salary certificate'),
        ('istiqdam_form','Istiqdam Form(Family Visa Letter)'),
        ('family_visa_letter','Family Visa Letter'),
        ('family_resident','Family Resident Visa Application'),
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
        'salary_certificate':'cascade',
        'istiqdam_form':'cascade',
        'family_resident':'cascade',
        'family_visa_letter':'cascade'
    }
    )

    state = fields.Selection(selection_add=[('coc_mofa_document', 'COC/MOFA Document')])
    
    # Bank Loan fields
    upload_bank_loan_doc = fields.Binary(string="Bank Loan Document")
    upload_bank_loan_doc_file_name = fields.Char(string="Bank Loan Document")
    bank_loan_doc_ref = fields.Char(string="Ref No.*")
    
    # Vehicle Lease fields
    upload_vehicle_lease_doc = fields.Binary(string="Letter for Vehicle lease")
    upload_vehicle_lease_doc_file_name = fields.Char(string="Letter for Vehicle lease")
    vehicle_lease_ref = fields.Char(string="Ref No.*")
    
    # Apartment Lease fields
    upload_apartment_lease_doc = fields.Binary(string="Letter for Apartment lease")
    upload_apartment_lease_doc_file_name = fields.Char(string="Letter for Apartment lease")
    apartment_lease_ref = fields.Char(string="Ref No.*")
    
    # Bank Letter fields
    upload_bank_letter_doc = fields.Binary(string="Bank Letter")
    upload_bank_letter_doc_file_name = fields.Char(string="Bank Letter")
    bank_letter_ref = fields.Char(string="Ref No.*")
    
    # Car Loan fields
    upload_car_loan_doc = fields.Binary(string="Car Loan Document")
    upload_car_loan_doc_file_name = fields.Char(string="Car Loan Document")
    car_loan_doc_ref = fields.Char(string="Ref No.*")
    
    # Rental Agreement fields
    upload_rental_agreement_doc = fields.Binary(string="Rental Agreement Document")
    upload_rental_agreement_doc_file_name = fields.Char(string="Rental Agreement Document")
    rental_agreement_doc_ref = fields.Char(string="Ref No.*")
    
    # Exception Letter fields
    upload_exception_letter_doc = fields.Binary(string="Exception Document")
    upload_exception_letter_doc_file_name = fields.Char(string="Exception Document")
    exception_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Attestation Waiver Letter fields
    upload_attestation_waiver_letter_doc = fields.Binary(string="Attestation Waiver Document")
    upload_attestation_waiver_letter_doc_file_name = fields.Char(string="Attestation Waiver Document")
    attestation_waiver_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Embassy Letter fields
    upload_embassy_letter_doc = fields.Binary(string="Embassy Letter")
    upload_embassy_letter_doc_file_name = fields.Char(string="Embassy Letter")
    embassy_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Istiqdam Letter fields
    upload_istiqdam_letter_doc = fields.Binary(string="Istiqdam Letter")
    upload_istiqdam_letter_doc_file_name = fields.Char(string="Istiqdam Letter")
    istiqdam_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # SCE Letter fields
    upload_sce_letter_doc = fields.Binary(string="SCE Letter")
    upload_sce_letter_doc_file_name = fields.Char(string="SCE Letter")
    sce_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Bilingual Salary Certificate fields
    upload_bilingual_salary_certificate_doc = fields.Binary(string="Bilingual Salary Certificate")
    upload_bilingual_salary_certificate_doc_file_name = fields.Char(string="Bilingual Salary Certificate")
    bilingual_salary_certificate_doc_ref = fields.Char(string="Ref No.*")
    
    # Contract Letter fields
    upload_contract_letter_doc = fields.Binary(string="Contract Letter")
    upload_contract_letter_doc_file_name = fields.Char(string="Contract Letter")
    contract_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Bank Account Opening Letter fields
    upload_bank_account_opening_letter_doc = fields.Binary(string="Bank account Opening Letter")
    upload_bank_account_opening_letter_doc_file_name = fields.Char(string="Bank account Opening Letter")
    bank_account_opening_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Bank Limit Upgrading Letter fields
    upload_bank_limit_upgrading_letter_doc = fields.Binary(string="Bank Limit upgrading Letter")
    upload_bank_limit_upgrading_letter_doc_file_name = fields.Char(string="Bank Limit upgrading Letter")
    bank_limit_upgrading_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Cultural Letter fields
    upload_cultural_letter_doc = fields.Binary(string="Cultural Letter")
    upload_cultural_letter_doc_file_name = fields.Char(string="Cultural Letter")
    cultural_letter_doc_ref = fields.Char(string="Ref No.*")
    
    # Employee Secondment fields
    upload_emp_secondment_or_cub_contra_ltr_doc = fields.Binary(string="Employee secondment / Subcontract Document")
    upload_emp_secondment_or_cub_contra_ltr_doc_file_name = fields.Char(string="Employee secondment / Subcontract Document")
    emp_secondment_ltr_doc_ref = fields.Char(string="Ref No.*")

    #Employment Contract
    upload_employment_contract_doc = fields.Binary(string="Employment Contract")
    upload_employment_contract_doc_file_name = fields.Char(string="Employment Contract")
    employment_contract_doc_ref = fields.Char(string="Ref No.*")

    #Salary Certificate
    upload_salary_certificate_doc = fields.Binary(string="Salary Certificate")
    upload_salary_certificate_doc_file_name = fields.Char(string="Salary Certificate")
    salary_certificate_ref = fields.Char(string="Ref No.*")

    #Istiqdam Form
    draft_istiqdam = fields.Binary(string="Draft Istiqdam",compute="auto_fill_istiqdam_form",store=True)
    updated_istiqdam_form_doc = fields.Binary(string="Updated Istiqdam Form")
    upload_istiqdam_form_doc_file_name = fields.Char(string="Updated Istiqdam Form")
    upload_istiqdam_form_doc = fields.Binary(string="Upload Istiqdam Form")
    istiqdam_form_doc_ref = fields.Char(string="Ref No.*")

    #Family Visa Letter
    upload_family_visa_letter_doc = fields.Binary(string="Family Visa Letter")
    upload_family_visa_letter_doc_file_name = fields.Char(string="Family Visa Letter")
    family_visa_letter_doc_ref = fields.Char(string="Ref No.*")

    #family resident
    upload_attested_application_doc = fields.Binary(string="Upload Attested Application")
    upload_attested_application_file_name = fields.Char(string="Attested Application")
    attested_application_doc_ref = fields.Char(string="Ref No.*")
    
   
    
    # Common fields for loan letters
    upload_saddad_doc = fields.Binary(string="Saddad Document")
    upload_saddad_doc_file_name = fields.Char(string="Saddad Document")
    saddad_doc_ref = fields.Char(string="Ref No.*")
    saddad_number = fields.Char(string="Saddad Number")
    upload_transcation_doc = fields.Binary(string="Transcation Document")
    upload_transcation_doc_file_name = fields.Char(string="Transcation Document")
    transcation_ref = fields.Char(string="Ref No.*")
    upload_mofa_doc = fields.Binary(string="MOFA Attested Document")
    upload_mofa_doc_file_name = fields.Char(string="MOFA Document")
    mofa_doc_ref = fields.Char(string="Ref No.*")

    show_mofa_section = fields.Boolean(
        string='Show MOFA Section',
        compute='_compute_show_mofa_section',
        store=False
    )

    @api.depends('letter_print_type_id')
    def _compute_show_mofa_section(self):
        for rec in self:
            rec.show_mofa_section = (
                rec.letter_print_type_id and
                len(rec.letter_print_type_id) == 1 and
                rec.letter_print_type_id[0].name == 'MOFA (Stamp)'
            )

    
    doc_uploaded = fields.Boolean(string="Document uploaded",default=False,copy=False)

    @api.onchange('upload_bank_loan_doc', 'dependent_document_ids','upload_vehicle_lease_doc',
                  'upload_apartment_lease_doc', 'upload_bank_letter_doc', 'upload_car_loan_doc',
                  'upload_rental_agreement_doc', 'upload_exception_letter_doc', 'upload_attestation_waiver_letter_doc',
                  'upload_embassy_letter_doc', 'upload_istiqdam_letter_doc', 'upload_sce_letter_doc',
                  'upload_bilingual_salary_certificate_doc', 'upload_contract_letter_doc',
                  'upload_bank_account_opening_letter_doc', 'upload_bank_limit_upgrading_letter_doc',
                  'upload_cultural_letter_doc', 'upload_emp_secondment_or_cub_contra_ltr_doc','upload_employment_contract_doc','salary_certificate','upload_istiqdam_form_doc','upload_attested_application_doc')
    def loan_letter_document_uploaded(self):
        for record in self:
            if record.service_request == 'bank_loan' and record.upload_bank_loan_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'vehicle_lease' and record.upload_vehicle_lease_doc:
                record.doc_uploaded = True
            elif record.service_request == 'apartment_lease' and record.upload_apartment_lease_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'bank_letter' and record.upload_bank_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'car_loan' and record.upload_car_loan_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'rental_agreement' and record.upload_rental_agreement_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'exception_letter' and record.upload_exception_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'attestation_waiver_letter' and record.upload_attestation_waiver_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'embassy_letter' and record.upload_embassy_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'istiqdam_letter' and record.upload_istiqdam_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'sce_letter' and record.upload_sce_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'bilingual_salary_certificate' and record.upload_bilingual_salary_certificate_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'contract_letter' and record.upload_contract_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'bank_account_opening_letter' and record.upload_bank_account_opening_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'bank_limit_upgrading_letter' and record.upload_bank_limit_upgrading_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'cultural_letter' and record.upload_cultural_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'emp_secondment_or_cub_contra_ltr' and record.upload_emp_secondment_or_cub_contra_ltr_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'employment_contract' and record.upload_employment_contract_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'salary_certificate' and record.upload_salary_certificate_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'istiqdam_form' and record.upload_istiqdam_form_doc and record.dependent_document_ids and record.upload_istiqdam_letter_doc:
                record.doc_uploaded = True
            elif record.service_request == 'family_resident' and record.upload_attested_application_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            elif record.service_request == 'family_visa_letter' and record.upload_family_visa_letter_doc and record.dependent_document_ids:
                record.doc_uploaded = True
            else:
                record.doc_uploaded = False 

    @api.depends('service_request')
    def auto_fill_istiqdam_form(self):
        for line in self:
            if line.service_request == 'istiqdam_form':
                istiqdam_id = self.env['visa.ref.documents'].search([('is_istiqdam_doc','=',True)],limit=1)
                line.draft_istiqdam = istiqdam_id.istiqdam_doc
            else:
                line.draft_istiqdam = False  
    
    @api.model
    def create(self, vals):
        employee_id = vals.get('employee_id')
        iqama_no = vals.get('iqama_no', 'UnknownIqama')
        service_request_config_id = vals.get('service_request_config_id')

        employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
        service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'

        if 'upload_bank_loan_doc' in vals:
            vals['upload_bank_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLoanLetter.pdf"
        if 'upload_saddad_doc' in vals:
            vals['upload_saddad_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SaddadDocument.pdf"
        if 'upload_vehicle_lease_doc' in vals:
            vals['upload_vehicle_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForVehicleLeaseDoc.pdf"
        if 'upload_apartment_lease_doc' in vals:
            vals['upload_apartment_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForAppartmentLeaseDoc.pdf"
        if 'upload_bank_letter_doc' in vals:
            vals['upload_bank_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLetterDoc.pdf"
        if 'upload_car_loan_doc' in vals:
            vals['upload_car_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CarLoanDoc.pdf"
        if 'upload_rental_agreement_doc' in vals:
            vals['upload_rental_agreement_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_RentalAgreementLetterDoc.pdf"
        if 'upload_exception_letter_doc' in vals:
            vals['upload_exception_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ExceptionLetterDoc.pdf"
        if 'upload_attestation_waiver_letter_doc' in vals:
            vals['upload_attestation_waiver_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestationWaiverLetterDoc.pdf"
        if 'upload_embassy_letter_doc' in vals:
            vals['upload_embassy_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmbassyLetterDoc.pdf"
        if 'upload_istiqdam_letter_doc' in vals:
            vals['upload_istiqdam_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamLetterDoc.pdf"
        if 'upload_sce_letter_doc' in vals:
            vals['upload_sce_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SCELetterDoc.pdf"
        if 'upload_bilingual_salary_certificate_doc' in vals:
            vals['upload_bilingual_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BillinugalSalaryCertifiacte.pdf"
        if 'upload_contract_letter_doc' in vals:
            vals['upload_contract_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ContractLetterDoc.pdf"
        if 'upload_bank_account_opening_letter_doc' in vals:
            vals['upload_bank_account_opening_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankAccountOpeningLetterDoc.pdf"
        if 'upload_bank_limit_upgrading_letter_doc' in vals:
            vals['upload_bank_limit_upgrading_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLimitUpgradingLetterDoc.pdf"
        if 'upload_cultural_letter_doc' in vals:
            vals['upload_cultural_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CulturalLetter.pdf"
        if 'upload_emp_secondment_or_cub_contra_ltr_doc' in vals:
            vals['upload_emp_secondment_or_cub_contra_ltr_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentorSubcontractDoc.pdf"
        if 'upload_employment_contract_doc' in vals:
            vals['upload_employment_contract_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentContractDoc.pdf"
        if 'upload_salary_certificate_doc' in vals:
            vals['upload_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SalaryCertificateDoc.pdf"
        if 'upload_istiqdam_form_doc' in vals:
            vals['upload_istiqdam_form_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamFormDoc.pdf"
        if 'upload_family_visa_letter_doc' in vals:
            vals['upload_family_visa_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisaLetter.pdf"
        if 'upload_attested_application_doc' in vals:
            vals['upload_attested_application_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestedApplication.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'

            if 'upload_bank_loan_doc' in vals:
                vals['upload_bank_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLoanLetter.pdf"
            if 'upload_saddad_doc' in vals:
                vals['upload_saddad_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SaddadDocument.pdf"
            if 'upload_vehicle_lease_doc' in vals:
                vals['upload_vehicle_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForVehicleLeaseDoc.pdf"
            if 'upload_apartment_lease_doc' in vals:
                vals['upload_apartment_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForAppartmentLeaseDoc.pdf"
            if 'upload_bank_letter_doc' in vals:
                vals['upload_bank_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLetterDoc.pdf"
            if 'upload_car_loan_doc' in vals:
                vals['upload_car_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CarLoanDoc.pdf"
            if 'upload_rental_agreement_doc' in vals:
                vals['upload_rental_agreement_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_RentalAgreementLetterDoc.pdf"
            if 'upload_exception_letter_doc' in vals:
                vals['upload_exception_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ExceptionLetterDoc.pdf"
            if 'upload_attestation_waiver_letter_doc' in vals:
                vals['upload_attestation_waiver_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestationWaiverLetterDoc.pdf"
            if 'upload_embassy_letter_doc' in vals:
                vals['upload_embassy_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmbassyLetterDoc.pdf"
            if 'upload_istiqdam_letter_doc' in vals:
                vals['upload_istiqdam_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamLetterDoc.pdf"
            if 'upload_sce_letter_doc' in vals:
                vals['upload_sce_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SCELetterDoc.pdf"
            if 'upload_bilingual_salary_certificate_doc' in vals:
                vals['upload_bilingual_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BillinugalSalaryCertifiacte.pdf"
            if 'upload_contract_letter_doc' in vals:
                vals['upload_contract_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ContractLetterDoc.pdf"
            if 'upload_bank_account_opening_letter_doc' in vals:
                vals['upload_bank_account_opening_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankAccountOpeningLetterDoc.pdf"
            if 'upload_bank_limit_upgrading_letter_doc' in vals:
                vals['upload_bank_limit_upgrading_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLimitUpgradingLetterDoc.pdf"
            if 'upload_cultural_letter_doc' in vals:
                vals['upload_cultural_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CulturalLetter.pdf"
            if 'upload_emp_secondment_or_cub_contra_ltr_doc' in vals:
                vals['upload_emp_secondment_or_cub_contra_ltr_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentorSubcontractDoc.pdf"
            if 'upload_employment_contract_doc' in vals:
                vals['upload_employment_contract_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentContractDoc.pdf"
            if 'upload_salary_certificate_doc' in vals:
                vals['upload_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SalaryCertificateDoc.pdf"
            if 'upload_istiqdam_form_doc' in vals:
                vals['upload_istiqdam_form_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IstiqdamFormDoc.pdf"
            if 'upload_family_visa_letter_doc' in vals:
                vals['upload_family_visa_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_FamilyVisaLetter.pdf"
            if 'upload_attested_application_doc' in vals:
                vals['upload_attested_application_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_AttestedApplication.pdf"
        return super(ServiceEnquiry, self).write(vals)

    def action_submit(self):
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request in ['bank_loan', 'vehicle_lease', 'apartment_lease', 'bank_letter', 'car_loan', 
                                       'rental_agreement', 'exception_letter', 'attestation_waiver_letter', 
                                       'embassy_letter', 'istiqdam_letter', 'sce_letter', 'bilingual_salary_certificate', 
                                       'contract_letter', 'bank_account_opening_letter', 'bank_limit_upgrading_letter',
                                       'cultural_letter', 'emp_secondment_or_cub_contra_ltr','employment_contract','salary_certificate','istiqdam_form','family_visa_letter','family_resident']:
                if not line.aamalcom_pay and not line.self_pay and not line.employee_pay:
                    raise ValidationError('Please select who needs to pay fees.')
                if line.aamalcom_pay and not (line.billable_to_client or line.billable_to_aamalcom):
                    raise ValidationError('Please select at least one billing detail when Fees to be paid by Aamalcom is selected.')
        
    def action_submit_payment_confirmation(self):
        super(ServiceEnquiry, self).action_submit_payment_confirmation()
        for line in self:
            if line.service_request in ['bank_loan', 'vehicle_lease', 'apartment_lease', 'bank_letter', 'car_loan', 
                                       'rental_agreement', 'exception_letter', 'attestation_waiver_letter', 
                                       'embassy_letter', 'istiqdam_letter', 'sce_letter', 'bilingual_salary_certificate', 
                                       'contract_letter', 'bank_account_opening_letter', 'bank_limit_upgrading_letter',
                                       'cultural_letter', 'emp_secondment_or_cub_contra_ltr','employment_contract','salary_certificate','istiqdam_form','family_visa_letter','family_resident']:
                line.dynamic_action_status = f'Payment done by client spoc. Document upload pending by first govt employee'
                line.action_user_id = line.first_govt_employee_id.user_id.id
                line.write({'processed_date': fields.Datetime.now()})

    def open_assign_employee_wizard_govt_employee(self):
        # This method opens the new assign employee wizard for loan letters
        for record in self:
            # --- Validation Checks---
            if record.service_request == 'vehicle_lease':
                if record.upload_vehicle_lease_doc and not record.vehicle_lease_ref:
                    raise ValidationError("Kindly Update Reference Number for Vehicle lease letter")
            if record.service_request == 'bank_loan':
                if record.upload_bank_loan_doc and not record.bank_loan_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank Loan letter")
            if record.service_request == 'apartment_lease':
                if record.upload_apartment_lease_doc and not record.apartment_lease_ref:
                    raise ValidationError("Kindly Update Reference Number for Apartment lease letter")
            if record.service_request == 'bank_letter':
                if record.upload_bank_letter_doc and not record.bank_letter_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank letter")
            if record.service_request == 'car_loan':
                if record.upload_car_loan_doc and not record.car_loan_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Car loan letter")
            if record.service_request == 'rental_agreement':
                if record.upload_rental_agreement_doc and not record.rental_agreement_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Rental agreement letter")
            if record.service_request == 'exception_letter':
                if record.upload_exception_letter_doc and not record.exception_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Exception letter")
            if record.service_request == 'attestation_waiver_letter':
                if record.upload_attestation_waiver_letter_doc and not record.attestation_waiver_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attestation Waiver letter")
            if record.service_request == 'embassy_letter':
                if record.upload_embassy_letter_doc and not record.embassy_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Embassy letter")
            if record.service_request == 'istiqdam_letter':
                if record.upload_istiqdam_letter_doc and not record.istiqdam_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Istiqdam Letter")
            if record.service_request == 'sce_letter':
                if record.upload_sce_letter_doc and not record.sce_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for SCE Letter")
            if record.service_request == 'bilingual_salary_certificate':
                if record.upload_bilingual_salary_certificate_doc and not record.bilingual_salary_certificate_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bilingual Salary Certificate")
            if record.service_request == 'contract_letter':
                if record.upload_contract_letter_doc and not record.contract_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Contract letter")
            if record.service_request == 'bank_account_opening_letter':
                if record.upload_bank_account_opening_letter_doc and not record.bank_account_opening_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank account Opening Letter")
            if record.service_request == 'bank_limit_upgrading_letter':
                if record.upload_bank_limit_upgrading_letter_doc and not record.bank_limit_upgrading_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank limit upgrading letter")
            if record.service_request == 'cultural_letter':
                if record.upload_cultural_letter_doc and not record.cultural_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Cultural Letter/Bonafide Letter")
            if record.service_request == 'emp_secondment_or_cub_contra_ltr':
                if record.upload_emp_secondment_or_cub_contra_ltr_doc and not record.emp_secondment_ltr_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Employee secondment / Subcontract letter")
            if record.service_request == 'employment_contract':
                if record.upload_employment_contract_doc and not record.employment_contract_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Employee Contract letter")
            if record.service_request == 'salary_certificate':
                if record.upload_salary_certificate_doc and not record.salary_certificate_ref:
                    raise ValidationError("Kindly Update Reference Number for Salary Certificate letter")
            if record.service_request == 'istiqdam_form':
                if record.upload_istiqdam_letter_doc and not record.istiqdam_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Istiqdam Letter")
                if record.upload_istiqdam_form_doc and not record.istiqdam_form_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Istiqdam Document")
            if record.service_request == 'family_visa_letter':
                if record.upload_family_visa_letter_doc and not record.family_visa_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Family visa letter") 
            if record.service_request == 'family_resident':
                if record.upload_attested_application_doc and not record.attested_application_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attested Visa Application")
                 
           
            # --- End Validation Checks ---
            department_ids = []
            # Simplified logic - always use level1
            level = 'level1'
            # Get departments from service request configuration
            if record.service_request_config_id and record.service_request_config_id.service_department_lines:
                req_lines = record.service_request_config_id.service_department_lines
                # Sort lines by sequence
                sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
                for lines in sorted_lines:
                    if lines.sequence == 1:  # Only get the first department
                        department_ids.append((4, lines.department_id.id))
                        break
            record.write({'processed_date': fields.Datetime.now()})
            return {
                'name': 'Assign Employee',
                'type': 'ir.actions.act_window',
                'res_model': 'assign.employee.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_department_ids': department_ids,
                    'default_assign_type': 'assign',
                    'default_levels': level
                },
            }

    def action_process_complete_without_mofa(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in ['bank_loan', 'vehicle_lease', 'apartment_lease', 'bank_letter', 'car_loan', 
                                         'rental_agreement', 'exception_letter', 'attestation_waiver_letter', 
                                         'embassy_letter', 'istiqdam_letter', 'sce_letter', 'bilingual_salary_certificate', 
                                         'contract_letter', 'bank_account_opening_letter', 'bank_limit_upgrading_letter',
                                         'cultural_letter', 'emp_secondment_or_cub_contra_ltr','employment_contract','salary_certificate','istiqdam_form','family_visa_letter','family_resident']:
                if record.service_request == 'vehicle_lease':
                    if record.upload_vehicle_lease_doc and not record.vehicle_lease_ref:
                        raise ValidationError("Kindly Update Reference Number for Vehicle lease letter")
                if record.service_request == 'bank_loan':
                    if record.upload_bank_loan_doc and not record.bank_loan_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Bank Loan letter")
                if record.service_request == 'apartment_lease':
                    if record.upload_apartment_lease_doc and not record.apartment_lease_ref:
                        raise ValidationError("Kindly Update Reference Number for Apartment lease letter")
                if record.service_request == 'bank_letter':
                    if record.upload_bank_letter_doc and not record.bank_letter_ref:
                        raise ValidationError("Kindly Update Reference Number for Bank letter")
                if record.service_request == 'car_loan':
                    if record.upload_car_loan_doc and not record.car_loan_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Car loan letter")
                if record.service_request == 'rental_agreement':
                    if record.upload_rental_agreement_doc and not record.rental_agreement_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Rental agreement letter")
                if record.service_request == 'exception_letter':
                    if record.upload_exception_letter_doc and not record.exception_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Exception letter")
                if record.service_request == 'attestation_waiver_letter':
                    if record.upload_attestation_waiver_letter_doc and not record.attestation_waiver_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Attestation Waiver letter")
                if record.service_request == 'embassy_letter':
                    if record.upload_embassy_letter_doc and not record.embassy_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Embassy letter")
                if record.service_request == 'istiqdam_letter':
                    if record.upload_istiqdam_letter_doc and not record.istiqdam_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Istiqdam Letter")
                if record.service_request == 'sce_letter':
                    if record.upload_sce_letter_doc and not record.sce_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for SCE Letter")
                if record.service_request == 'bilingual_salary_certificate':
                    if record.upload_bilingual_salary_certificate_doc and not record.bilingual_salary_certificate_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Bilingual Salary Certificate")
                if record.service_request == 'contract_letter':
                    if record.upload_contract_letter_doc and not record.contract_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Contract letter")
                if record.service_request == 'bank_account_opening_letter':
                    if record.upload_bank_account_opening_letter_doc and not record.bank_account_opening_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Bank account Opening Letter")
                if record.service_request == 'bank_limit_upgrading_letter':
                    if record.upload_bank_limit_upgrading_letter_doc and not record.bank_limit_upgrading_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Bank limit upgrading letter")
                if record.service_request == 'cultural_letter':
                    if record.upload_cultural_letter_doc and not record.cultural_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Cultural Letter/Bonafide Letter")
                if record.service_request == 'emp_secondment_or_cub_contra_ltr':
                    if record.upload_emp_secondment_or_cub_contra_ltr_doc and not record.emp_secondment_ltr_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Employee secondment / Subcontract letter")
                if record.service_request == 'employment_contract':
                    if record.upload_employment_contract_doc and not record.employment_contract_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Employee Contract letter")
                if record.service_request == 'salary_certificate':
                    if record.upload_salary_certificate_doc and not record.salary_certificate_ref:
                        raise ValidationError("Kindly Update Reference Number for Salary Certificate letter")
                if record.service_request == 'istiqdam_form':
                    if record.upload_istiqdam_letter_doc and not record.istiqdam_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Istiqdam Letter")
                    if record.upload_istiqdam_form_doc and not record.istiqdam_form_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Istiqdam Document")
                if record.service_request == 'family_visa_letter':
                    if record.upload_family_visa_letter_doc and not record.family_visa_letter_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Family visa letter") 
                if record.service_request == 'family_resident':
                    if record.upload_attested_application_doc and not record.attested_application_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Attested Visa Application")
                     
                record.state='done'
                record.dynamic_action_status='Process Completed'
                record.action_user_id=False  
                record.write({'processed_date': fields.Datetime.now()})     
    
     

    def action_process_complete(self):
        super(ServiceEnquiry, self).action_process_complete()
        for record in self:
            if record.service_request in ['bank_loan', 'vehicle_lease', 'apartment_lease', 'bank_letter', 'car_loan', 
                                         'rental_agreement', 'exception_letter', 'attestation_waiver_letter', 
                                         'embassy_letter', 'istiqdam_letter', 'sce_letter', 'bilingual_salary_certificate', 
                                         'contract_letter', 'bank_account_opening_letter', 'bank_limit_upgrading_letter',
                                         'cultural_letter', 'emp_secondment_or_cub_contra_ltr','employment_contract','salary_certificate','istiqdam_form','family_visa_letter','family_resident']:
                if record.upload_saddad_doc and not record.saddad_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Saddad Document")
                if not record.saddad_number:
                    raise ValidationError("Kindly Update Saddad Number")
                if record.upload_transcation_doc and not record.transcation_ref:
                    raise ValidationError("Kindly Update Reference Number for Transcation Document")
                if record.upload_mofa_doc and not record.mofa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for MOFA Document")
                record.state='done'
                record.dynamic_action_status='Process Completed'
                record.action_user_id=False  
                record.write({'processed_date': fields.Datetime.now()}) 
                