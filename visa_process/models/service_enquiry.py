# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceEnquiry(models.Model):
    _name = 'service.enquiry'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Service Enquiry"

    

    name = fields.Char(string="Enquiry No")
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")
    
    client_id = fields.Many2one('res.partner',string="Client Spoc",default=lambda self: self.env.user.partner_id)
    client_parent_id = fields.Many2one('res.partner',string="Client",default=lambda self: self.env.user.partner_id.parent_id)
    # priority = fields.Selection([
    #     ('clear','Clear'),
    #     ('urgent', 'Urgent'),
    #     ('normal', 'Normal'),
    #     ('lowand', 'Lowand'),
    #     ('high','High')],
    #     copy=False, default='normal', required=True)

    # below values are updated on change of service request
    approver_id = fields.Many2one('hr.employee',string="Approver",copy=False)
    approver_user_id = fields.Many2one('res.users',string="Approver User Id",copy=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Ticket Submitted'),
        ('waiting_client_approval', 'Waiting Client Spoc Approval'),
        ('client_approved','Approved by Client Spoc'),
        ('waiting_op_approval','Waiting OH Approval'),
        ('waiting_gm_approval','Waiting GM Approval'),
        ('waiting_fin_approval','Waiting FM Approval'),
        ('approved','Approved'),
        ('payment_initiation','Payment Initiation'),
        ('payment_done','Payment Confirmation'),
        ('done', 'Completed'),('refuse','Refuse'),('cancel','Cancel')], string='State',default="draft",copy=False,tracking=True)
    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa'),('twv_request','Temporary Work Visa')],string="Service Request Type",tracking=True,copy=False)
    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request_type','=',service_request_type)]",copy=False)
    process_type = fields.Selection([('automatic','Automatic'),('manual','Manual')],string="Process Type",default="manual",copy=False)
    dynamic_action_status = fields.Char('Action Status', readonly=True, default='Draft')
    submit_clicked = fields.Boolean(string="Submit Clicked", default=False)
    latest_existing_request_id = fields.Boolean(string='Latest Existing Request ID',default=False,copy=False)
    latest_existing_request_name = fields.Char(string='Latest Existing Request Name', readonly=True,copy=False)

    @api.onchange('service_request_config_id')
    def update_process_type(self):
        for line in self:
            if line.service_request_config_id:
                line.process_type = line.service_request_config_id.process_type
            # Passing the latest existing request name in the alert message for visibility,
            if line.service_request_config_id and line.employee_id:
                latest_existing_request = self.search([
                    ('employee_id', '=', line.employee_id.id),
                    ('service_request_config_id', '=', line.service_request_config_id.id)
                ], limit=1)
                if latest_existing_request:
                    if latest_existing_request:
                        line.latest_existing_request_id = True
                        line.latest_existing_request_name = latest_existing_request.display_name
    service_request = fields.Selection([('new_ev','Issuance of New EV'),
        ('sec','SEC Letter'),('hr_card','Issuance for HR card'),('transfer_req','Transfer Request Initiation'),

        ('ins_class_upgrade','Medical health insurance Class Upgrade'),
        ('iqama_no_generation','Iqama Card Generation'),('iqama_card_req','New Physical Iqama Card Request'),
        ('qiwa','Qiwa Contract'),('gosi','GOSI Update'),('iqama_renewal','Iqama Renewal'),
        ('prof_change_qiwa','Profession change Request In qiwa'),('salary_certificate','Salary certificate'),
        ('bank_letter','Bank letter'),('vehicle_lease','Letter for Vehicle Lease'),
        ('apartment_lease','Letter for Apartment Lease'),
        ('employment_contract','Employment contract'),
        ('cultural_letter','Cultural Letter/Bonafide Letter'),
        ('emp_secondment_or_cub_contra_ltr','Employee secondment / Subcontract letter'),
        ('car_loan','Car Loan Letter'),('rental_agreement','Rental Agreement Letter'),
        ('exception_letter','Exception Letter'),('attestation_waiver_letter','Attestation Waiver Letter'),
        ('embassy_letter','Embassy Letters- as Per Respective Embassy requirement'),('istiqdam_letter','Istiqdam Letter'),
        ('sce_letter','SCE Letter'),('bilingual_salary_certificate','Bilingual Salary Certificate'),('contract_letter','Contract Letter'),
        ('bank_account_opening_letter','Bank account Opening Letter'),('bank_limit_upgrading_letter','Bank Limit upgrading Letter'),
        ('final_exit_issuance','Final exit Issuance'),
        ('dependent_transfer_query','Dependent Transfer Query'),('soa','Statement of account till date')],string="Service Requests",related="service_request_config_id.service_request",store=True,copy=False)
    
    employee_id = fields.Many2one('hr.employee',domain="[('custom_employee_type', '=', 'external'),('client_id','=',user_id)]",string="Employee",store=True,tracking=True,required=True,copy=False)
    iqama_no = fields.Char(string="Iqama No")
    identification_id = fields.Char(string='Border No.')
    passport_no = fields.Char(string='Passport No')
    sponsor_id = fields.Many2one('employee.sponsor',string="Sponsor Number",tracking=True,copy=False,store=True)



    transfer_type = fields.Selection([('to_aamalcom','To Aamalcom'),('to_another_establishment','To another Establishment')],string="Transfer Type")
    transfer_amount = fields.Float(string="Amount")

    is_penalty_applicable = fields.Boolean(string="Is Penalty Applicable?",copy=False)
    penalty_cost = fields.Float(string="Penalty Cost",copy=False)
    

    priority = fields.Selection([
        ('0', 'No Priority'), ('1', 'Low'),
        ('2', 'Medium'), ('3', 'High')],
        'Priority',default=0)

    @api.onchange('employee_id')
    def update_service_request_type_from_employee(self):
        for line in self:
            if line.employee_id:
                line.service_request_type = line.employee_id.service_request_type
                line.iqama_no = line.employee_id.iqama_no
                line.identification_id = line.employee_id.identification_id
                line.passport_no = line.employee_id.passport_id

    emp_visa_id = fields.Many2one('employment.visa',string="Service Id",tracking=True,domain="[('employee_id','=',employee_id)]")




    # LT Fields
    bank_id = fields.Many2one('res.bank',string="Bank")
    purpose = fields.Text(string="Purpose?")
    letter_print_type_id = fields.Many2many('letter.print.type',string="Type")
    letter_cost = fields.Monetary(string="Letter Cost",compute="_compute_total_cost",store=True)

    @api.depends('letter_print_type_id.cost')
    def _compute_total_cost(self):
        for record in self:
            cost = sum(record.letter_print_type_id.mapped('cost'))
            record.letter_cost = cost

    draft_if_any = fields.Binary(string="Draft if any")
    coc_certification = fields.Selection([('yes','Yes'),('no','No')],string="COC Certification")
    re_entry_issuance = fields.Selection([('single','Single'),('multiple','Multiple')],string="Re-entry issuance")
    from_date = fields.Date(string="From Date")
    valid_reason = fields.Text(string="Valid reason to be stated")
    any_credit_note = fields.Text(string="Any credit note to be issued with reason")
    
    insurance_availability = fields.Selection([('yes','Yes'),('no','No')],string="Medical Insurance")
    medical_doc = fields.Binary(string="Medical Doc")

    upload_hr_card = fields.Binary(string="HR Card Document")
    upload_hr_card_file_name = fields.Char(string="HR Card Document")
    hr_card_ref = fields.Char(string="Ref No.*")
    reupload_hr_card = fields.Binary(string="Updated HR Card Document")
    reupload_hr_card_file_name = fields.Char(string="Updated HR Card Document")
    rehr_card_ref = fields.Char(string="Ref No.*")
    upload_jawazat_doc = fields.Binary(string="Jawazat Document")
    upload_jawazat_doc_file_name = fields.Char(string="Jawazat Document")
    jawazat_doc_ref = fields.Char(string="Ref No.*")
    upload_sponsorship_doc = fields.Binary(string="Confirmation of Sponsorship")
    upload_sponsorship_doc_file_name = fields.Char(string="Confirmation of Sponsorship")
    sponsorship_doc_ref = fields.Char(string="Ref No.*")
    upload_payment_doc = fields.Binary(string="Payment Confirmation Document",tracking=True)
    upload_payment_doc_file_name = fields.Char(string="Payment Confirmation Document",tracking=True)
    payment_doc_ref = fields.Char(string="Ref No.*")
    residance_doc = fields.Binary(string="Residance Permit Document")
    residance_doc_file_name = fields.Char(string="Residance Permit Document")
    residance_doc_ref = fields.Char(string="Ref No.*")
    transfer_confirmation_doc = fields.Binary(string="Confirmation of Transfer")
    transfer_confirmation_doc_file_name = fields.Char(string="Confirmation of Transfer")
    transfer_confirmation_ref = fields.Char(string="Ref No.*")
    muqeem_print_doc = fields.Binary(string="Muqeem Print Document")
    muqeem_print_doc_file_name = fields.Char(string="Muqeem Print Document")
    muqeem_print_doc_ref = fields.Char(string="Ref No.*")

    upload_upgrade_insurance_doc = fields.Binary(string="Confirmation of Insurance upgarde Document")
    upload_upgrade_insurance_doc_file_name = fields.Char(string="Confirmation of Insurance upgarde Document")
    upgarde_ins_doc_ref = fields.Char(string="Ref No.*")

    request_date = fields.Datetime(string="Request Date",default=fields.Datetime.now)

    upload_iqama_card_doc = fields.Binary(string="Upload Iqama Card")
    upload_iqama_card_doc_file_name = fields.Char(string="Upload Iqama Card")
    iqama_card_ref = fields.Char(string="Ref No.*")
    upload_iqama_card_no_doc = fields.Binary(string="Upload Iqama Card")
    upload_iqama_card_no_doc_file_name = fields.Binary(string="Upload Iqama Card")
    iqama_card_no_ref = fields.Char(string="Ref No.*")
    upload_qiwa_doc = fields.Binary(string="Upload Qiwa Contract")
    upload_qiwa_doc_file_name = fields.Char(string="Qiwa Card")
    qiwa_doc_ref = fields.Char(string="Ref No.*")
    upload_gosi_doc = fields.Binary(string="Upload GOSI Update")
    upload_gosi_doc_file_name=fields.Char(string="GOSI Update")
    gosi_doc_ref = fields.Char(string="Ref No.*")
    profession_change_doc = fields.Binary(string="Profession Change Req. Doc")
    profession_change_doc_file_name = fields.Char(string="Profession Change Doc")
    profession_change_doc_ref = fields.Char(string="Ref No.*")
    profession_change_final_doc = fields.Binary(string="Profession Change Req. Doc")
    profession_change_final_doc_file_name = fields.Char(string="Profession Change Req. Doc")
    prof_change_final_ref = fields.Char(string="Ref No.*")
    upload_salary_certificate_doc = fields.Binary(string="Salary Certificate")
    upload_salary_certificate_doc_file_name = fields.Char(string="Salary Certificate")
    salary_certificate_ref = fields.Char(string="Ref No.*")
    upload_bank_letter_doc = fields.Binary(string="Bank Letter")
    upload_bank_letter_doc_file_name = fields.Char(string="Bank Letter")
    bank_letter_ref = fields.Char(string="Ref No.*")
    upload_vehicle_lease_doc = fields.Binary(string="Letter for Vehicle lease")
    upload_vehicle_lease_doc_file_name = fields.Char(string="Letter for Vehicle lease")
    vehicle_lease_ref = fields.Char(string="Ref No.*")
    upload_apartment_lease_doc = fields.Binary(string="Letter for Apartment lease")
    upload_apartment_lease_doc_file_name = fields.Char(string="Letter for Apartment lease")
    apartment_lease_ref = fields.Char(string="Ref No.*")
    
    upload_employment_contract_doc = fields.Binary(string="Employment Contract")
    upload_employment_contract_doc_file_name = fields.Char(string="Employment Contract")
    employment_contract_doc_ref = fields.Char(string="Ref No.*")
    upload_cultural_letter_doc = fields.Binary(string="Cultural Letter")
    upload_cultural_letter_doc_file_name= fields.Char(string="Cultural Letter")
    cultural_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_final_exit_issuance_doc = fields.Binary(string="Final Exit issuance doc")
    upload_final_exit_issuance_doc_file_name = fields.Char(string="Final Exit issuance doc")

    final_exit_issuance_doc_ref = fields.Char(string="Ref No.*")
    upload_soa_doc = fields.Binary(string="SOA Doc")
    upload_soa_doc_file_name = fields.Char(string="SOA Doc")
    soa_doc_ref = fields.Char(string="Ref No.*")
    upload_emp_secondment_or_cub_contra_ltr_doc = fields.Binary(string="Employee secondment / Subcontract Document")
    upload_emp_secondment_or_cub_contra_ltr_doc_file_name = fields.Char(string="Employee secondment / Subcontract Document")
    emp_secondment_ltr_doc_ref = fields.Char(string="Ref No.*")
    upload_car_loan_doc = fields.Binary(string="Car Loan Document")
    upload_car_loan_doc_file_name = fields.Char(string="Car Loan Document")
    car_loan_doc_ref = fields.Char(string="Ref No.*")
    
    upload_rental_agreement_doc = fields.Binary(string="Rental Agreement Document")
    upload_rental_agreement_doc_file_name = fields.Char(string="Rental Agreement Document")
    rental_agreement_doc_ref = fields.Char(string="Ref No.*")
    upload_exception_letter_doc = fields.Binary(string="Exception Document")
    upload_exception_letter_doc_file_name = fields.Char(string="Exception Document")
    exception_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_attestation_waiver_letter_doc = fields.Binary(string="Attestation Waiver Document")
    upload_attestation_waiver_letter_doc_file_name = fields.Char(string="Attestation Waiver Document")
    attestation_waiver_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_embassy_letter_doc = fields.Binary(string="Embassy Letter")
    upload_embassy_letter_doc_file_name = fields.Char(string="Embassy Letter")
    embassy_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_istiqdam_letter_doc = fields.Binary(string="Istiqdam Letter")
    upload_istiqdam_letter_doc_file_name= fields.Char(string="Istiqdam Letter")
    istiqdam_letter_doc_ref = fields.Char(string="Ref No.*")
    # upload_sce_letter_doc = fields.Binary(string="SCE Letter")
    upload_bilingual_salary_certificate_doc = fields.Binary(string="Bilingual Salary Certificate")
    upload_bilingual_salary_certificate_doc_file_name = fields.Char(string="Bilingual Salary Certificate")
    bilingual_salary_certificate_doc_ref = fields.Char(string="Ref No.*")
    upload_contract_letter_doc = fields.Binary(string="Contract Letter")
    upload_contract_letter_doc_file_name = fields.Char(string="Contract Letter")
    contract_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_bank_account_opening_letter_doc = fields.Binary(string="Bank account Opening Letter")
    upload_bank_account_opening_letter_doc_file_name = fields.Char(string="Bank account Opening Letter")
    bank_account_opening_letter_doc_ref = fields.Char(string="Ref No.*")
    upload_bank_limit_upgrading_letter_doc = fields.Binary(string="Bank Limit upgrading Letter")
    upload_bank_limit_upgrading_letter_doc_file_name = fields.Char(string="Bank Limit upgrading Letter")
    bank_limit_upgrading_letter_doc_ref = fields.Char(string="Ref No.*")

    
    reason_for_loss_of_iqama = fields.Text(string="Reason for loss of Iqama")
    letter_from_police_station = fields.Binary(string="Letter from the police station of the lost iqama")
    note = fields.Text(string="Note",default="Note: Cost 1000 sar, invoice not available")
    visit_visa_note = fields.Text(string="Note",default="Note: Document will be Attested by COC ")
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")


    # EV Fields
    old_ev_id = fields.Many2one(
        'service.enquiry',
        string="Ref SR-EV",
        domain="[('service_request', '=', 'new_ev'), ('state', '=', 'done'),('employee_id','=',employee_id)]",
       
    )
    visa_country_id = fields.Many2one('res.country',string="Visa issuing country")
    visa_state_id = fields.Char(string="Visa issuing city")
    visa_religion = fields.Selection([('muslim','Muslim'),('non_muslim','Non-Muslim'),('others','Others')],string="Visa Religion")
    no_of_visa = fields.Integer(string="No of Visa")
    profession = fields.Char(string="Profession",tracking=True)
    agency_allocation = fields.Text(string="Allocation of Agency (E wakala)")
    coc_for_ewakala = fields.Boolean(string="COC for Ewakala",compute="update_coc_for_ewakala",store=True)

    upload_issuance_doc = fields.Binary(string="Upload Issuance of Visa Document")
    upload_issuance_doc_file_name = fields.Char(string="Upload Issuance of Visa Document")
    issuance_doc_ref = fields.Char(string="Ref No.*")
    upload_proof_of_request_doc = fields.Binary(string="Upload Proof of Request Document")
    upload_proof_of_request_file_name = fields.Char(string="Proof of Request  Document")
    proof_of_request_ref = fields.Char(string="Ref No.*")
    upload_enjaz_doc = fields.Binary(string="Enjaz Document")
    upload_enjaz_doc_file_name = fields.Char(string="Enjaz Document")
    enjaz_doc_ref = fields.Char(string="Ref No.*")
    e_wakala_doc = fields.Binary(string="E Wakala Document")
    e_wakala_doc_file_name = fields.Char(string="E Wakala Document")
    e_wakala_doc_ref = fields.Char(string="Ref No.*")
    upload_sec_doc = fields.Binary(string="SEC Letter")
    upload_sec_doc_file_name = fields.Char(string="SEC Letter")
    sec_doc_ref = fields.Char(string="Ref No.*")

    visa_document = fields.Binary(string="Visa Document")
    chamber = fields.Selection([('yes','Yes'),('no','No')],string="Chamber")
    mofa_draft = fields.Binary(string="Draft")
    mofa_reason = fields.Text(string="Reason for issuing the letter")
    sec_draft = fields.Binary(string="Draft")
    coc = fields.Selection([('yes','Yes'),('no','No')],string="COC")
    sec_upload = fields.Binary(string="Document Upload")
    cost_difference = fields.Selection([('aamalcom','Aamalcom'),('lti','LTI')],string="Cost Difference")


    # Common fields
    employment_duration = fields.Many2one('employment.duration',string="Duration",tracking=True,domain="[('service_request_type','=',service_request_type),('service_request_config_id','=',service_request_config_id)]")

    
    self_bill_string = fields.Char(string="Self Bill String", compute="_compute_self_bill_string")
    self_pay = fields.Boolean(string="Self")

    aamalcom_pay_string = fields.Char(string="Aamalcom Pay String", compute="_compute_self_bill_string")
    aamalcom_pay = fields.Boolean(string="Aamalcom")

    employee_pay_string = fields.Char(string="Employee Pay String")
    employee_pay = fields.Boolean(string="Employee")

    self_bill = fields.Boolean(string="Self")
    billable_to_client_string = fields.Char(string="Billable to Client",compute="_compute_self_bill_string")
    billable_to_client = fields.Boolean(string="Billable to Client")

    billable_to_aamalcom_string = fields.Char(string="Billable to Aamalcom",compute="_compute_self_bill_string")
    billable_to_aamalcom = fields.Boolean(string="Billable to Aamalcom")

    current_insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Current Insurance Class")
    class_to_be_changed = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Class to be changed to!")
    duration_limit = fields.Selection([('30','30'),('60','60'),('90','90'),('120','120'),('150','150'),('180','180'),('210','210'),('240','240'),('270','270'),('300','300'),('330','330'),('360','360')],string="Duration")


    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Current Insurance Class")

    document_upload = fields.Binary(string="Document Upload")
    logical_reason = fields.Text(string="Logical Reason to be stated")
    border_id_doc = fields.Binary(string="Upload Iqama /Passport with border ID")
    iqama_upload = fields.Binary(string="Iqama Upload")
    profession_change = fields.Char(string="Profession change to")
    soa_date = fields.Date(string="Duration")
    duration = fields.Char(string="Duration")

    fee_receipt_doc = fields.Binary(string="Fee Receipt Document")
    fee_receipt_doc_file_name = fields.Char(string="Fee Receipt File Name")
    fee_receipt_doc_ref = fields.Char(string="Ref No.*")

    confirmation_doc = fields.Binary(string="Confirmation Document")
    confirmation_doc_file_name = fields.Char(string="Confirmation Document File Name")
    confirmation_doc_ref = fields.Char(string="Ref No.*")


    # EV fields
    dob = fields.Date(string="DOB",tracking=True)
    contact_no = fields.Char(string="Contact # in the country",tracking=True)
    current_contact = fields.Char(string="Current Contact # (if Outside the country) *",tracking=True)
    email = fields.Char(string="Email Id *",tracking=True)
    nationality_id = fields.Many2one('res.country',string="Nationality",tracking=True)
    phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")
    current_phone_code_id = fields.Many2one('res.partner.phonecode',string="Phone code")

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
    # Employment details
    designation = fields.Char(string="Designation on Offer Letter",tracking=True)
    doj = fields.Date(string="Projected Date of Joining",tracking=True)
    
    probation_term = fields.Char(string="Probation Term",tracking=True,copy=False)
    notice_period = fields.Char(string="Notice Period",tracking=True,copy=False)
    working_days = fields.Char(string="Working Days *",copy=False)
    working_hours = fields.Char(string="Working Hours *",copy=False)
    annual_vacation = fields.Char(string="Annual Vacation *",copy=False)
    weekly_off_days = fields.Char(string="Weekly Off (No. Of Days)",tracking=True,copy=False)

    # # Documents
    signed_offer_letter = fields.Binary(string="Signed Offer letter/should be attached *",copy=False)
    passport_copy = fields.Binary(string="Passport copy *",copy=False)
    border_copy = fields.Binary(string="Border Id *",copy=False)
    attested_degree = fields.Binary(string="Attested Degree copy *",copy=False)
    attested_visa_page = fields.Binary(string="Attested visa page *",copy=False)
    bank_iban_letter = fields.Binary(string="Bank Iban Letter *",copy=False)
    certificate_1 = fields.Binary(string="Certificates *",copy=False)
    certificate_2 = fields.Binary(string="Certificates",copy=False)
    other_doc_1 = fields.Binary(string="Others",copy=False)
    other_doc_2 = fields.Binary(string="Others",copy=False)
    other_doc_3 = fields.Binary(string="Others",copy=False)
    other_doc_4 = fields.Binary(string="Others",copy=False)
    
    
    


    # Profession Details
    visa_profession = fields.Char(string="Visa Profession *")
    hr_agency = fields.Char(string="Agency")
    
    visa_nationality_id = fields.Many2one('res.country',string="Visa Nationality *")
    visa_stamping_city_id = fields.Char(string="Visa Stamping City *")
    visa_enjaz = fields.Char(string="Visa Enjaz Details *")
    no_of_visa = fields.Integer(string="No of Visa *")
    visa_fees = fields.Selection([('aamalcom','Aamalcom'),('lti','LTI')],string="Visa Fees")
    visa_gender = fields.Selection([('male','Male'),('female','Female'),('others','Others')],string="Visa Gender *")
    qualification = fields.Char(string="Education Qualification *",copy=False)

    iqama_designation = fields.Char(string="Designation on Iqama (exact)",copy=False)
    attested_from_saudi_cultural = fields.Selection([('yes','Yes'),('no','No')],string="Degree attested from saudi cultural",copy=False)
    

    # Air Fare
    air_fare_for = fields.Selection([('self','Self'),('family','Family')],string="Air Fare for?")
    air_fare_frequency = fields.Char(string="Air Fare Frequency")

    # Medical Insurance
    medical_insurance_for = fields.Selection([('self','Self'),('family','Family')],string="Medical Insurance For?",copy=False)
    
    dependent_document_ids = fields.One2many('dependent.documents','ev_enq_dependent_document_id',string="Dependent Documents")

    service_enquiry_pricing_ids = fields.One2many('service.enquiry.pricing.line','service_enquiry_id',copy=False)

    total_amount = fields.Monetary(string="Total Amount" , readonly=True, compute="_compute_amount")

    
    assign_govt_emp_one = fields.Boolean(string="Assign First Govt Employee",copy=False)
    assigned_govt_emp_one = fields.Boolean(string="Assigned First Govt Employee",copy=False)
    assign_govt_emp_two = fields.Boolean(string="Assign Second Govt Employee",copy=False)
    assigned_govt_emp_two = fields.Boolean(string="Assigned Second Govt Employee",copy=False)
    first_govt_employee_id = fields.Many2one('hr.employee',string="1st Government Employee",tracking=True,copy=False)
    second_govt_employee_id = fields.Many2one('hr.employee',string="2nd Government Employee",tracking=True,copy=False)
   

    current_department_ids = fields.Many2many('hr.department','service_enquiry_dept_ids',string="Department",compute="update_departments")

    req_completion_date = fields.Datetime(string="Request Completion Date",copy=False)

    # below fields are to track the approvers

    op_approver_id = fields.Many2one('hr.employee',string="Approved Operation Manager",copy=False)
    gm_approver_id = fields.Many2one('hr.employee',string="Approved General Manager",copy=False)
    fin_approver_id = fields.Many2one('hr.employee',string="Approved Finance Manager",copy=False)

    request_note = fields.Text(string="Request Query",copy=False)  

    doc_uploaded = fields.Boolean(string="Document uploaded",default=False,copy=False)
    second_level_doc_uploaded = fields.Boolean(string="Second Leve Document uploaded",default=False,copy=False)
    final_doc_uploaded = fields.Boolean(string="Final Document uploaded",default=False,copy=False)
    total_treasury_requests = fields.Integer(string="Request Details",compute="_compute_total_treasury_requests")

    is_service_request_client_spoc = fields.Boolean(
        string="Is Service Request Client SPOC",
        compute='_compute_is_service_request_client_spoc'
    )

    #used for readonly attribute - should be entered only pm 
    is_project_manager = fields.Boolean(
        compute='_compute_is_project_manager',
        store=False,
        default=False
    )

    refuse_reason = fields.Text(string="Refuse Reason", readonly=True,tracking=True)

    @api.depends('is_project_manager')
    def _compute_is_project_manager(self):
        for record in self:
            # Check if the logged-in user belongs to the 'group_service_request_manager'
            record.is_project_manager = self.env.user.has_group('visa_process.group_service_request_manager')

    #used for  readonly attribute - should be entered by the first government employee
    is_gov_employee = fields.Boolean(compute='_compute_is_gov_employee', store=False)


    @api.depends('is_gov_employee')
    def _compute_is_gov_employee(self):
        for record in self:
            # Check if the user is in gov employee groups
            record.is_gov_employee = self.env.user.has_group('visa_process.group_service_request_employee')



    @api.depends('user_id.groups_id','state','service_request_config_id')
    def _compute_is_service_request_client_spoc(self):
        """Compute function to check if the user belongs to group_service_request_client_spoc"""
        client_spoc_group = self.env.ref('visa_process.group_service_request_client_spoc')
        aamalcom_spoc_group = self.env.ref('visa_process.group_service_request_manager')
        fin_group = self.env.ref('visa_process.group_service_request_finance_manager')
        req_admin = self.env.ref('visa_process.group_service_request_administrator')
        for record in self:
            is_client_spoc = client_spoc_group in record.env.user.groups_id
            is_aamalcom_spoc = aamalcom_spoc_group in record.env.user.groups_id
            is_fin_group = fin_group in record.env.user.groups_id
            is_req_admin = req_admin in record.env.user.groups_id
            record.is_service_request_client_spoc = is_client_spoc or is_aamalcom_spoc or is_fin_group or is_req_admin

    def action_doc_uplaod_submit(self):
        for record in self:
            if record.service_request == 'hr_card':
                if record.reupload_hr_card and not record.rehr_card_ref:
                    raise ValidationError("Kindly Update Reference Number for Re-upload HR Document")
                record.state = 'approved'
                record.dynamic_action_status = f"Document uploaded by 1st Govt employee, PM needs to assign 2nd Govt Employee"
                record.submit_clicked = True

            

    # @api.onchange('emp_visa_id')
    # def update_employee_id(self):
    #     for line in self:
    #         line.employee_id = line.emp_visa_id.employee_id

    @api.depends('agency_allocation')
    def update_coc_for_ewakala(self):
        for line in self:
            if line.agency_allocation:
                line.coc_for_ewakala = True
            else:
                line.coc_for_ewakala = False
    

    @api.onchange('self_pay')
    def update_fees_paid_by_self(self):
        for line in self:
            if line.self_pay == True:
                line.aamalcom_pay = False
                line.employee_pay = False
    @api.onchange('aamalcom_pay')
    def update_fees_paid_by_aamalcom(self):
        for line in self:
            if line.aamalcom_pay == True:
                line.self_pay = False
                line.employee_pay = False
            else:
                line.billable_to_client = False
                line.billable_to_aamalcom = False

    @api.onchange('employee_pay')
    def update_fees_paid_by_employee(self):
        for line in self:
            if line.employee_pay == True:
                line.aamalcom_pay = False
                line.self_pay = False
    
    
    @api.depends('client_id')
    def _compute_self_bill_string(self):
        for record in self:
            if record.client_id:
                record.self_bill_string = f"{record.client_id.parent_id.name}"
                record.billable_to_client_string = f"{record.client_id.parent_id.name}"
                record.billable_to_aamalcom_string = "Aamalcom"
                record.aamalcom_pay_string = "Aamalcom"
                record.employee_pay_string = f"{record.employee_id.name}"
            else:
                record.self_bill_string = False
                record.billable_to_client_string = False
                record.billable_to_aamalcom_string = False
                record.aamalcom_pay_string = False
                record.employee_pay_string = False
    #Code to rename the filename 

    @api.model
    def create(self, vals):
        if 'upload_car_loan_doc' in vals:
            employee_id = vals.get('employee_id')  # Assuming employee_id is a Many2one field
            iqama_no = vals.get('iqama_no', 'UnknownIqama')
            service_request_config_id = vals.get('service_request_config_id')  # Assuming service_request_config_id is a Many2one field
            employee_name = self.env['hr.employee'].browse(employee_id).name if employee_id else 'UnknownEmployee'
            service_request_name = self.env['service.request.config'].browse(service_request_config_id).name if service_request_config_id else 'UnknownServiceRequest'
            vals['upload_car_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CarLoanDoc.pdf"
        if 'upload_issuance_doc' in vals:
            vals['upload_issuance_doc_file_name']=f"{employee_name}_{iqama_no}_{service_request_name}_Issuance of Visa Document.pdf"
        if 'upload_proof_of_request_doc' in vals:
            vals['upload_proof_of_request_file_name']=f"{employee_name}_{iqama_no}_{service_request_name}_ProofOfRequestDoc.pdf"
        if 'upload_payment_doc' in vals:
            vals['upload_payment_doc_file_name']=f"{employee_name}_{iqama_no}_{service_request_name}_PaymentConfirmationDocument.pdf"
        if 'upload_enjaz_doc' in vals:
            vals['upload_enjaz_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazDocument.pdf"
        if 'e_wakala_doc' in vals:
            vals['e_wakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EwakalaDocument.pdf"
        if 'upload_hr_card' in vals:
            vals['upload_hr_card_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_HRCard.pdf"
        if 'reupload_hr_card' in vals:
            vals['reupload_hr_card_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_UpdatedHRDoc.pdf"
        if 'residance_doc' in vals:
            vals['residance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ResidancePermitDoc.pdf"
        if 'muqeem_print_doc' in vals:
            vals['muqeem_print_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPrintDocument.pdf"
        if 'upload_upgrade_insurance_doc' in vals:
            vals['upload_upgrade_insurance_doc_field_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_InsuranceupgardeDocument.pdf"
        if 'upload_iqama_card_no_doc' in vals:
            vals['upload_iqama_card_no_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IqamaCard.pdf"
        if 'upload_iqama_card_doc' in vals:
            vals['upload_iqama_card_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IqamaCard.pdf"
        if 'upload_qiwa_doc' in vals:
            vals['upload_qiwa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_QiwaDocument.pdf"
        if 'upload_gosi_doc' in vals:
            vals['upload_gosi_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_GOSIUpdate.pdf"
        if 'profession_change_doc' in vals:
            vals['profession_change_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ProfessionChangeDoc.pdf"
        if 'profession_change_final_doc_' in vals:
            vals['profession_change_final_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ProfessionFinalChangeDoc.pdf"
        if 'upload_salary_certificate_doc' in vals:
            vals['upload_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SalaryCertificateDoc.pdf"
        if 'upload_bank_letter_doc' in vals:
            vals['upload_bank_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLetterDoc.pdf"
        if 'upload_vehicle_lease_doc' in vals:
            vals['upload_vehicle_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForVehicleLeaseDoc.pdf"
        if 'upload_apartment_lease_doc' in vals:
            vals['upload_apartment_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForAppartmentLeaseDoc.pdf"
        if 'upload_employment_contract_doc' in vals:
            vals['upload_employment_contract_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentContractDoc.pdf"
        if 'upload_cultural_letter_doc' in vals:
            vals['upload_cultural_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CulturalLetter.pdf"
        if 'upload_sec_doc' in vals:
            vals['upload_sec_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SECDoc.pdf"
        if 'upload_emp_secondment_or_cub_contra_ltr_doc' in vals:
            vals['upload_emp_secondment_or_cub_contra_ltr_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentorSubcontractDoc.pdf"
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
        if 'upload_bilingual_salary_certificate_doc' in vals:
            vals['upload_bilingual_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BillinugalSalaryCertifiacte.pdf"
        if 'upload_contract_letter_doc' in vals:
            vals['upload_contract_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ContractLetterDoc.pdf"
        if 'upload_bank_account_opening_letter_doc' in vals:
            vals['upload_bank_account_opening_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankAccountOpeningLetterDoc.pdf"
        if 'upload_bank_limit_upgrading_letter_doc' in vals:
            vals['upload_bank_limit_upgrading_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLimitUpgradingLetterDoc.pdf"
        if 'transfer_confirmation_doc' in vals:
            vals['transfer_confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_TransferConfirmationDoc.pdf"
        if 'upload_jawazat_doc' in vals:
            vals['upload_jawazat_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_JawazatDoc.pdf"
        if 'upload_sponsorship_doc' in vals:
            vals['upload_sponsorship_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SponsorshipDoc.pdf"
        return super(ServiceEnquiry, self).create(vals)

    def write(self, vals):
        for record in self:
            employee_name = record.employee_id.name if record.employee_id else 'UnknownEmployee'
            iqama_no = record.iqama_no or 'UnknownIqama'
            service_request_name = record.service_request_config_id.name if record.service_request_config_id else 'UnknownServiceRequest'
            if 'upload_car_loan_doc' in vals:
                vals['upload_car_loan_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CarLoanDoc.pdf"
            if 'upload_issuance_doc' in vals:
                vals['upload_issuance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IssuanceDocument.pdf"
            if 'upload_proof_of_request_doc' in vals:
                vals['upload_proof_of_request_file_name']=f"{employee_name}_{iqama_no}_{service_request_name}_ProofOfRequestDoc.pdf"    
            if 'upload_payment_doc' in vals:
                vals['upload_payment_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_PaymentConfirmationDocument.pdf"
            if 'upload_enjaz_doc' in vals:
                vals['upload_enjaz_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EnjazDocument.pdf"
            if 'e_wakala_doc' in vals:
                vals['e_wakala_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EwakalaDocument.pdf"
            if 'upload_hr_card' in vals:
                vals['upload_hr_card_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_HR Card.pdf"
            if 'reupload_hr_card' in vals:
                vals['reupload_hr_card_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_UpdatedHRDoc.pdf"
            if 'residance_doc' in vals:
                vals['residance_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ResidancePermitDoc.pdf"
            if 'muqeem_print_doc' in vals:
                vals['muqeem_print_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_MuqeemPrintDocument.pdf"
            if 'upload_upgrade_insurance_doc' in vals:
                vals['upload_upgrade_insurance_doc_field_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_Insurance upgarde Document.pdf"
            if 'upload_iqama_card_no_doc' in vals:
                vals['upload_iqama_card_no_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IqamaCard.pdf"
            if 'upload_iqama_card_doc' in vals:
                vals['upload_iqama_card_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_IqamaCard.pdf"
            if 'upload_qiwa_doc' in vals:
                vals['upload_qiwa_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_QiwaDocument.pdf"
            if 'upload_gosi_doc' in vals:
                vals['upload_gosi_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_GOSIUpdate.pdf"
            if 'profession_change_doc' in vals:
                vals['profession_change_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ProfessionChangeDoc.pdf"
            if 'profession_change_final_doc_' in vals:
                vals['profession_change_final_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ProfessionFinalChangeDoc.pdf"
            if 'upload_salary_certificate_doc' in vals:
                vals['upload_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SalaryCertificateDoc.pdf"
            if 'upload_bank_letter_doc' in vals:
                vals['upload_bank_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLetterDoc.pdf"
            if 'upload_vehicle_lease_doc' in vals:
                vals['upload_vehicle_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForVehicleLeaseDoc.pdf"
            if 'upload_apartment_lease_doc' in vals:
                vals['upload_apartment_lease_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_LetterForAppartmentLeaseDoc.pdf"
            if 'upload_employment_contract_doc' in vals:
                vals['upload_employment_contract_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentContractDoc.pdf"
            if 'upload_cultural_letter_doc' in vals:
                vals['upload_cultural_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_CulturalLetter.pdf"
            if 'upload_sec_doc' in vals:
                vals['upload_sec_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SECDoc.pdf"
            if 'upload_emp_secondment_or_cub_contra_ltr_doc' in vals:
                vals['upload_emp_secondment_or_cub_contra_ltr_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_EmploymentorSubcontractDoc.pdf"
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
            if 'upload_bilingual_salary_certificate_doc' in vals:
                vals['upload_bilingual_salary_certificate_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BillinugalSalaryCertifiacte.pdf"
            if 'upload_contract_letter_doc' in vals:
                vals['upload_contract_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_ContractLetterDoc.pdf"
            if 'upload_bank_account_opening_letter_doc' in vals:
                vals['upload_bank_account_opening_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankAccountOpeningLetterDoc.pdf"
            if 'upload_bank_limit_upgrading_letter_doc' in vals:
                vals['upload_bank_limit_upgrading_letter_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_BankLimitUpgradingLetterDoc.pdf"
            if 'transfer_confirmation_doc' in vals:
                vals['transfer_confirmation_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_TransferConfirmationDoc.pdf"
            if 'upload_jawazat_doc' in vals:
                vals['upload_jawazat_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_JawazatDoc.pdf"
            if 'upload_sponsorship_doc' in vals:
                vals['upload_sponsorship_doc_file_name'] = f"{employee_name}_{iqama_no}_{service_request_name}_SponsorshipDoc.pdf"
        return super(ServiceEnquiry, self).write(vals)

    @api.depends('state', 'service_request_config_id')
    def update_departments(self):
        # this method fetches departments configured in service request based on hierarchy
        for line in self:
            department_ids = []
            if line.service_request_config_id.service_department_lines:
                if not line.service_request_config_id.service_request == 'iqama_card_req':
                    line.current_department_ids = False
                    for lines in line.service_request_config_id.service_department_lines:
                        if line.state in (
                                'submitted', 'waiting_gm_approval', 'waiting_op_approval', 'waiting_fin_approval',
                                'waiting_client_approval'):
                            if lines.sequence == 1:
                                # line.current_department_id = lines.department_id.id
                                department_ids.append((4, lines.department_id.id))
                                line.current_department_ids = department_ids
                                break
                            else:
                                line.current_department_ids = False
                        elif line.state in ('payment_done', 'approved', 'client_approved'):
                            if line.service_request == 'new_ev' and line.state == 'approved' and line.assign_govt_emp_two == False:
                                if lines.sequence == 1:
                                    # line.current_department_id = lines.department_id.id
                                    department_ids.append((4, lines.department_id.id))
                                    line.current_department_ids = department_ids
                            if line.service_request == 'new_ev' and line.state == 'approved' and line.assign_govt_emp_two == True:
                                if lines.sequence == 2:
                                    # line.current_department_id = lines.department_id.id
                                    department_ids.append((4, lines.department_id.id))
                                    line.current_department_ids = department_ids

                            if not line.service_request == 'new_ev':
                                if lines.sequence == 2:
                                    # line.current_department_id = lines.department_id.id
                                    department_ids.append((4, lines.department_id.id))
                                    line.current_department_ids = department_ids
                                    break
                                else:
                                    line.current_department_ids = False
                        else:
                            line.current_department_ids = False
                else:
                    for lines in line.service_request_config_id.service_department_lines:
                        department_ids.append((4, lines.department_id.id))
                    line.current_department_ids = department_ids
                    break
            else:
                line.current_department_ids = False

    def open_assign_employee_wizard(self):
        # this method opens a wizard and passes department based on the hierarchy set in service request

        for line in self:
            treasury_id = self.env['service.request.treasury'].search([('service_request_id','=',line.id)])
            if treasury_id:
                for srt in treasury_id:
                    if srt.state != 'done':
                        raise ValidationError(_('Action required by Finance team. Kindly upload Confirmation Document provided by Treasury Department before continuing further'))

            # department_ids = [(6, 0, self.current_department_ids.ids)]
            department_ids = []
            if line.service_request == 'new_ev':
                if line.state == 'submitted':
                    level = 'level1'
                if line.state == 'payment_done':
                    level = 'level2'
                if line.state == 'approved' and line.assign_govt_emp_two == False:
                    level = 'level1'
                if line.state == 'approved' and line.assign_govt_emp_two != False:
                    level = 'level2'
            elif line.service_request =='iqama_card_req':
                if line.state == 'payment_done':
                    level = 'level1'

            else:
                if line.state == 'submitted':
                    level = 'level1'
                else:
                    level = 'level2'

            req_lines = line.service_request_config_id.service_department_lines
            # Sort lines by sequence
            sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
            for lines in sorted_lines:
                if level == 'level1':
                    department_ids.append((4, lines.department_id.id))
                    break  # Exit the loop after adding the first department for level1
                else:
                    if lines.sequence == 2:  # Only append the second department for level2
                        department_ids.append((4, lines.department_id.id))
            return {
                'name': 'Select Employee',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_department_ids': department_ids,'default_assign_type':'assign','default_levels':level},
            }

    def open_reassign_employee_wizard(self):
        department_ids = []
        for line in self:
            if line.service_request == 'new_ev':
                if line.state == 'submitted':
                    level = 'level1'
                if line.state == 'payment_done':
                    level = 'level2'
                if line.state == 'approved' and line.assign_govt_emp_two == False:
                    level = 'level1'
                if line.state == 'approved' and line.assign_govt_emp_two != False:
                    level = 'level2'

            else:
                if line.state == 'submitted':
                    level = 'level1'
                else:
                    level = 'level2'
            req_lines = line.service_request_config_id.service_department_lines
            # Sort lines by sequence
            sorted_lines = sorted(req_lines, key=lambda line: line.sequence)
            for lines in sorted_lines:
                if level == 'level1':
                    department_ids.append((4, lines.department_id.id))
                    break  # Exit the loop after adding the first department for level1
                else:
                    if lines.sequence == 2:  # Only append the second department for level2
                        department_ids.append((4, lines.department_id.id))
            return {
                    'name': 'Select Employee',
                    'type': 'ir.actions.act_window',
                    'res_model': 'employee.selection.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_department_ids': department_ids,'default_assign_type':'reassign','default_levels':'level2'},
                }

    @api.depends('service_enquiry_pricing_ids.amount')
    def _compute_amount(self):
        total_amount = 0.0
        for line in self:
            for lines in line.service_enquiry_pricing_ids:
                total_amount += lines.amount

            line.total_amount = total_amount  

    @api.onchange('billable_to_client')
    def update_billable_to_aamalcom(self):
        for line in self:
            if line.billable_to_client:
                line.billable_to_aamalcom = False

    @api.onchange('billable_to_aamalcom')
    def update_billable_to_client(self):
        for line in self:
            if line.billable_to_aamalcom:
                line.billable_to_client = False

    @api.onchange("service_request_config_id")
    def update_billing_booleans(self):
        for line in self:
            line.aamalcom_pay = False
            line.self_pay = False




    def update_pricing(self):
        for record in self:
            record.service_enquiry_pricing_ids = False
            pricing_id = self.env['service.pricing'].search([('service_request_type', '=', record.service_request_type),
                    ('service_request', '=', record.service_request)], limit=1)
            # iqama_card_req - payment will be collected offline
            # if record.aamalcom_pay and record.service_request == 'transfer_req' or record.service_request != 'iqama_card_req':
            if record.aamalcom_pay and record.service_request == 'new_ev' or record.service_request == 'hr_card' or record.service_request == 'iqama_renewal' or record.service_request == 'prof_change_qiwa':
                if pricing_id:
                    for p_line in pricing_id.pricing_line_ids:
                        if p_line.duration_id == record.employment_duration:
                            record.service_enquiry_pricing_ids.create({
                                'name':pricing_id.name,
                                'service_enquiry_id':record.id,
                                'service_pricing_id':pricing_id.id,
                                'service_pricing_line_id':p_line.id,
                                'amount':p_line.amount,
                                'remarks':p_line.remarks
                                })
                        if record.service_request == 'new_ev':
                            # need to check if they are going to enter duration for pricing.
                            # there will be a issue if they add multiple lines in pricing,
                            # instead its better to have duration for New Visa.
                            # or they need to be very cautious in adding pricing
                            record.service_enquiry_pricing_ids.create({
                                'name':pricing_id.name,
                                'service_enquiry_id':record.id,
                                'service_pricing_id':pricing_id.id,
                                'service_pricing_line_id':p_line.id,
                                'amount':p_line.amount,
                                'remarks':p_line.remarks
                                })
                else:
                    raise ValidationError(_('Service Pricing is not configured properly. Kindly contact your Accounts Manager'))
            if record.letter_print_type_id:
                for print_type in record.letter_print_type_id:
                    record.service_enquiry_pricing_ids.create({
                        'name': print_type.name,  # Assuming this is the name you want to set
                        'amount': print_type.cost,  # Assuming letter_cost is a field in the current record
                        'service_enquiry_id': record.id,
                    })
            if record.service_request == 'transfer_req':
                record.service_enquiry_pricing_ids.create({
                    'name':record.service_request_config_id.name,
                    'amount':record.transfer_amount,
                    'service_enquiry_id':record.id,
                    })
            if record.is_penalty_applicable == True:
                record.service_enquiry_pricing_ids.create({
                    'name':'Penalty Charges',
                    'amount':record.penalty_cost,
                    'service_enquiry_id':record.id,
                    })
           


    # LT Issuance of HR Card and Iqama renewal start

    def action_submit(self):
        for line in self:
            if line.service_request == 'new_ev' or line.service_request == 'transfer_req':
                if not line.aamalcom_pay and not line.self_pay:
                    raise ValidationError('Please select who needs to pay fees.')
            if line.aamalcom_pay and not (line.billable_to_client or line.billable_to_aamalcom):
                raise ValidationError('Please select at least one billing detail when Fees to be paid by Aamalcom is selected.')
            line.state = 'submitted'
            line.doc_uploaded = False
            if line.service_request:
                line.assign_govt_emp_one = True
            if line.service_request != 'transfer_req':
                self.update_pricing()
            self._add_followers()
            self.send_email_to_pm()
            if line.service_request == 'new_ev':
                line.dynamic_action_status = f"Submit for approval by PM"
            elif line.service_request == 'iqama_card_req':
                line.dynamic_action_status = f"Require confirmation on payment made by PM"
            else:
                line.dynamic_action_status = f"Employee needs to be assigned by PM"

    def action_require_payment_confirmation(self):
        for line in self:
            # passing error is ref no is not passed.
            if line.service_request =='new_ev':
                if line.state=='submitted' and line.self_pay == True:
                    if not line.issuance_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Issuance of Visa Document")

            if line.service_request in ('hr_card','iqama_renewal'):
                if line.state=='submitted' and line.self_pay == True:
                    if not line.hr_card_ref:
                        raise ValidationError("Kindly Update Reference Number for Hr Card Document")
            if line.service_request == 'prof_change_qiwa':
                if line.state=='submitted':
                    if line.profession_change_doc and not line.profession_change_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Profession Change Request Document")
            if line.service_request == 'transfer_req':
                if line.state=='submitted':
                    if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                        raise ValidationError("Kindly Update Reference Number for Confirmation of Transfer")
                    if line.upload_qiwa_doc and not line.qiwa_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Qiwa Contract")

            line.state = 'payment_initiation'
            line.dynamic_action_status = f"Requesting Payment confirmation Document by client spoc"
            line.doc_uploaded = False

            

    def action_new_ev_require_payment_confirmation(self):
        for line in self:
            line.state = 'payment_initiation'
            line.dynamic_action_status = f"Requesting Payment confirmation Document by client spoc"
            line.doc_uploaded = False


    def action_new_ev_submit_for_approval(self):
        for line in self:
            if line.service_request == 'new_ev':
                if line.state in ('submitted'):
                    if not line.proof_of_request_ref:
                        if not line.upload_proof_of_request_doc:
                            raise ValidationError("Kindly Update Proof of Request Document")
                    if not line.proof_of_request_ref:
                        raise ValidationError("Kindly Update Reference Number for Proof of Request Document")
            line.state = 'waiting_op_approval'

            # group = self.env.ref('visa_process.group_service_request_operations_manager')
            # users = group.users
            # user_names = ' or '.join(users.mapped('name'))
            # line.dynamic_action_status = f'Waiting for approval by : {user_names}'
            line.dynamic_action_status = "Waiting for approval by OM"

            self.send_email_to_op()

    def action_submit_for_approval(self):
        for line in self:
            if line.service_request in ('hr_card','iqama_renewal'):
                if line.state=='submitted' and (line.billable_to_client == True or line.billable_to_aamalcom==True):
                    if not line.hr_card_ref:
                        raise ValidationError("Kindly Update Reference Number for Hr Card Document")
            if line.service_request == 'prof_change_qiwa':
                if line.state=='submitted':
                    if line.profession_change_doc and not line.profession_change_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Profession Change Request Document")

            if line.service_request == 'transfer_req':
                if line.state=='submitted':
                    if line.transfer_confirmation_doc and not line.transfer_confirmation_ref:
                        raise ValidationError("Kindly Update Reference Number for Confirmation of Transfer")
                    if line.upload_qiwa_doc and not line.qiwa_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Qiwa Contract")

            if line.service_request == 'transfer_req':
                line.state = 'waiting_client_approval'
                line.dynamic_action_status = f'Waiting for approval by client spoc'
            else:
                line.state = 'waiting_op_approval'
                line.dynamic_action_status = "Waiting for approval by OM"
                self.send_email_to_op()

    def action_client_spoc_approve(self):
        for line in self:
            line.state = 'client_approved'
            line.assign_govt_emp_two = True
            # Approved by {self.env.user.name}.
            line.dynamic_action_status = f'Approved by client spoc. Second govt employee needs to be assigned by PM'


    @api.model
    def send_email_to_gm(self):
        group = self.env.ref('visa_process.group_service_request_general_manager')
        users = group.mapped('users')

        # Create the custom email body with the button link
        record_name = self.name or 'Service Request'
        body_html = """
            <p>Hi,</p>
            <p>You have a new Service Request to approve.</p>
            <p><strong>Service Request:</strong> %s</p>
            <p><a href="%s">View Service Request</a></p>
        """ % (record_name, self._get_record_url()) 

        # Send email to each user in the group
        for user in users:
            # Create a new email with the custom body
            mail_values = {
                'subject': 'Service Request - %s for approval' % record_name,
                'email_to': user.partner_id.email,
                'body_html': body_html,
                # 'email_from': current_user.email,
                'email_cc': [self.client_id.company_spoc_id.user_id.email],
                'reply_to': user.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()

    @api.model
    def send_email_to_op(self):
        group = self.env.ref('visa_process.group_service_request_operations_manager')
        users = group.mapped('users')
        # current_user = self.env.user

        # Create the custom email body with the button link
        record_name = self.name or 'Service Request'
        body_html = """
            <p>Hi,</p>
            <p>You have a new Service Request to approve.</p>
            <p><strong>Service Request:</strong> %s</p>
            <p><a href="%s">View Service Request</a></p>
        """ % (record_name, self._get_record_url()) 

        # Send email to each user in the group
        for user in users:
            # Create a new email with the custom body
            mail_values = {
                'subject': 'Service Request - %s for approval' % record_name,
                'email_to': user.partner_id.email,
                'body_html': body_html,
                # 'email_from': current_user.email,
                'email_cc': [self.client_id.company_spoc_id.user_id.email],
                'reply_to': user.partner_id.email,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()

    @api.model
    def send_email_to_pm(self):
        # Create the custom email body with the button link
        for line in self:
            current_user = self.env.user
            record_name = line.name or 'Service Request'
            body_html = """
                <p>Hi,</p>
                <p>You have a new Service Request to process:</p>
                <p><strong>Service Request:</strong> %s</p>
                <p><a href="%s">View Service Request</a></p>
            """ % (record_name, self._get_record_url()) 

            # Send email to each user in the group
        
            # Create a new email with the custom body
            
            mail_values = {
                'subject': 'New Service Request - %s' % record_name,
                'email_to': self.client_id.company_spoc_id.user_id.email,
                'body_html': body_html,
                'email_from': current_user.email,
                'reply_to': self.client_id.company_spoc_id.user_id.email,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()

    def _get_record_url(self):
        """Helper method to get the URL of the current record."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"

    def action_op_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]

        for line in self:
            line.state = 'waiting_gm_approval'
            line.op_approver_id = current_employee

            # group = self.env.ref('visa_process.group_service_request_general_manager')
            # users = group.users
            # user_names = ' or '.join(users.mapped('name'))
            # line.dynamic_action_status =  f"Waiting for approval by:{user_names}"
            line.dynamic_action_status =  "Waiting for approval by GM"

            self.send_email_to_gm()

    def action_gm_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for line in self:
            line.state = 'waiting_fin_approval'
            line.gm_approver_id = current_employee

            # group = self.env.ref('visa_process.group_service_request_finance_manager')
            # users = group.users
            # user_names = ' or '.join(users.mapped('name'))
            # line.dynamic_action_status = f'Waiting for approval by: {user_names}'
            line.dynamic_action_status = f'Waiting for approval by FM'

    def action_request_fin_payment_confirmation(self):
        for line in self:
            if line.transfer_amount == 0:
                raise ValidationError(_('Kindly enter transfer amount'))
            if line.upload_jawazat_doc and not line.jawazat_doc_ref:
                raise ValidationError("Kindly Update Reference Number for Jawazat Document")


            line.state = 'waiting_op_approval'
            line.dynamic_action_status = "Waiting for approval by OM"
            self.update_pricing()
            self.send_email_to_op()

    def action_finance_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for line in self:
            vals = {
            'service_request_id': self.id,
            'client_id': self.client_id.id,
            'client_parent_id':self.client_id.parent_id.id,
            'employee_id':self.employee_id.id,
            'employment_duration':self.employment_duration.id,
            'total_amount':self.total_amount
            }
            service_request_treasury_id = self.env['service.request.treasury'].sudo().create(vals)

            if service_request_treasury_id:
                line.state = 'approved'
                line.fin_approver_id = current_employee

                # group = self.env.ref('visa_process.group_service_request_finance_manager')
                # users = group.users
                # user_names = ' or '.join(users.mapped('name'))
                # line.dynamic_action_status = f'Need approval to submit the treasury confirmation document - FM: {user_names}'
                line.dynamic_action_status = f'Submission pending for the treasury department by FM'

                if line.service_request == 'hr_card' or line.service_request == 'iqama_renewal' or line.service_request == 'prof_change_qiwa':
                    line.assign_govt_emp_two = True
                if line.service_request == 'transfer_req':
                    line.state = 'payment_done'
                    # if line.billable_to_aamalcom == True:
                    #     line.assign_govt_emp_two = True
                if line.service_request == 'new_ev':
                    line.assign_govt_emp_one = True

    def action_new_ev_docs_uploaded(self):
        for line in self:
            if line.service_request =='new_ev':
                if line.state=='approved' and line.aamalcom_pay == True and (line.billable_to_aamalcom == True or line.billable_to_client == True):
                    if not line.issuance_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Issuance of Visa Document")
            line.assign_govt_emp_two = True
            line.dynamic_action_status = f"Second govt employee needs to be assigned by PM"
            # If a government employee or pm updates the sponsor number when issuing a new EV, it should automatically update the sponsor ID in that particular employee's master record.
            if line.employee_id and line.service_request == 'new_ev':
                if not line.employee_id.sponsor_id:
                    line.employee_id.sudo().write({'sponsor_id': self.sponsor_id})
                else:
                    line.sponsor_id = line.employee_id.sponsor_id

    def _add_followers(self):
        """
            Add Approver as followers
        """
        partner_ids = []
        if self.approver_id:
            partner_ids.append(self.approver_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)




    def action_submit_payment_confirmation(self):
        for line in self:
            if line.service_request in ('new_ev','hr_card','iqama_renewal','prof_change_qiwa','transfer_req') and line.state == 'payment_initiation':
                if not line.payment_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Payment Confirmation  Document")

            # if line.service_request =='prof_change_qiwa':
            #     line.dynamic_action_status = f'Payment done by {line.client_id.name}. Process to be completed by {line.first_govt_employee_id.name}'
            # else:
            line.dynamic_action_status = f'Payment done by client spoc. Second govt employee need to be assigned by PM'

            line.state = 'payment_done'
            line.doc_uploaded = False
            if line.service_request == 'hr_card' or line.service_request == 'iqama_renewal' or line.service_request == 'new_ev' or line.service_request == 'transfer_req'  or line.service_request == 'prof_change_qiwa':
                line.assign_govt_emp_two = True
            # if line.service_request == 'prof_change_qiwa':
            #     # line.doc_uploaded = True

    

    # LT Issuance of HR Card and Iqama Renewal end



    # LT Medical Health Insurance Upload start

    def action_submit_initiate(self):
        for line in self:
            line.state = 'submitted'
            line.dynamic_action_status = f"Employee needs to be assigned by PM"
            if line.service_request:
                line.assign_govt_emp_one = True
            self.update_pricing()
            self._add_followers()

    def action_process_complete(self):
        for line in self:
            if line.service_request == 'new_ev':
                if line.state in ('payment_done','approved'):
                    if not line.enjaz_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Enzaj Document")
                    if not line.e_wakala_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for E Wakala Document")
                    # If a government employee or pm updates the sponsor number when issuing a new EV, it should automatically update the sponsor ID in that particular employee's master record.
                    if line.employee_id and line.sponsor_id:
                        if not line.employee_id.sponsor_id:
                            line.employee_id.sudo().write({'sponsor_id': line.sponsor_id})
                        else:
                            line.sponsor_id = line.employee_id.sponsor_id
            if line.service_request =='hr_card':
                if line.state in ('payment_done','approved'):
                    if not line.rehr_card_ref:
                        raise ValidationError("Kindly Update Reference Number for Updated HR Document")
                    if not line.residance_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Residance Permit Document")
                    if not line.muqeem_print_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Muqeem Print Document")
            if line.service_request =='iqama_renewal':
                if line.state in ('payment_done','approved'):
                    if not line.residance_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Residance Permit Document")
                    if not line.muqeem_print_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Muqeem Print Document")
            if line.service_request == 'transfer_req':
                if line.state =='payment_done' and line.self_pay == True:
                    if not line.jawazat_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Jawazat Document")
                    if not line.sponsorship_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Confirmation of Sponsorship Document")
                    if not line.muqeem_print_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Muqeem Print Document")
                if line.state == 'payment_done' and (line.billable_to_client==True or line.billable_to_aamalcom==True):
                    if not line.jawazat_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Jawazat Document")
                    if not line.sponsorship_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Confirmation of Sponsorship Document")
                    if not line.muqeem_print_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Muqeem Print Document")
                    if not line.payment_doc_ref:
                        raise ValidationError("Kindly Update Reference Number for Payment Confirmation Document")

            if line.service_request in ('bank_account_opening_letter','bank_limit_upgrading_letter','final_exit_issuance','istiqdam_letter','bilingual_salary_certificate','contract_letter','exception_letter','attestation_waiver_letter','embassy_letter','rental_agreement','car_loan','bank_loan','emp_secondment_or_cub_contra_ltr','cultural_letter','employment_contract','apartment_lease','vehicle_lease','bank_letter','gosi','sec','ins_class_upgrade','iqama_no_generation','qiwa','salary_certificate'):
                if line.upload_upgrade_insurance_doc and not line.upgarde_ins_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation of Insurance upgarde Document")
                if line.upload_iqama_card_no_doc and not line.iqama_card_no_ref:
                    raise ValidationError("Kindly Update Reference Number for Iqama Card Document")
                if line.upload_qiwa_doc and not line.qiwa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Contract Document")
                if line.upload_salary_certificate_doc and not line.salary_certificate_ref:
                    raise ValidationError("Kindly Update Reference Number for Salary Certificate Document")
                if line.upload_sec_doc and not line.sec_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for SEC Letter Document")
                if line.upload_gosi_doc and not line.gosi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Gosi Letter Document")
                if line.upload_bank_letter_doc and not line.bank_letter_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank letter")
                if line.upload_vehicle_lease_doc and not line.vehicle_lease_ref:
                    raise ValidationError("Kindly Update Reference Number for Vehicle lease letter")
                if line.upload_apartment_lease_doc and not line.apartment_lease_ref:
                    raise ValidationError("Kindly Update Reference Number for Apartment lease letter")
                if line.upload_istiqdam_letter_doc and not line.istiqdam_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Istiqdam Letter")
                if line.upload_employment_contract_doc and not line.employment_contract_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Employment Contract")
                if line.upload_cultural_letter_doc and not line.cultural_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Cultural Letter/Bonafide Letter")
                if line.upload_emp_secondment_or_cub_contra_ltr_doc and not line.emp_secondment_ltr_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Employee secondment / Subcontract letter")
                if line.upload_car_loan_doc and not line.car_loan_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Car loan letter")
                if line.upload_rental_agreement_doc and not line.rental_agreement_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Rental agreement letter")
                if line.upload_exception_letter_doc and not line.exception_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Exception letter")
                if line.upload_attestation_waiver_letter_doc and not line.attestation_waiver_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Attestation Waiver letter")
                if line.upload_embassy_letter_doc and not line.embassy_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Embassy letter")
                if line.upload_bilingual_salary_certificate_doc and not line.bilingual_salary_certificate_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bilingual Salary Certificate")
                if line.upload_contract_letter_doc and not line.contract_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Contract letter")
                if line.upload_bank_account_opening_letter_doc and not line.bank_account_opening_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank account Opening Letter")
                if line.upload_bank_limit_upgrading_letter_doc and not line.bank_limit_upgrading_letter_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Bank limit upgrading letter")
                if line.upload_final_exit_issuance_doc and not line.final_exit_issuance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Final exit issuance document")
            if line.service_request == 'prof_change_qiwa':
                if not line.prof_change_final_ref:
                    raise ValidationError("Kindly Update Reference Number for Profession Change Document")
                if not line.muqeem_print_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Muqeem Print Document")
                treasury_id = self.env['service.request.treasury'].search([('service_request_id','=',line.id)])
                if treasury_id:
                    for srt in treasury_id:
                        if srt.state != 'done':
                            raise ValidationError(_('Action required by Finance team. Kindly upload Confirmation Document provided by Treasury Department before continuing further'))
                        else:
                            line.state = 'done'
                            line.req_completion_date = fields.Datetime.now()
                            line.dynamic_action_status = f"Process Completed"
                else:
                    line.state = 'done'
                    line.req_completion_date = fields.Datetime.now()
                    line.dynamic_action_status = f"Process Completed"
            else:
                line.state = 'done'
                line.dynamic_action_status = f"Process Completed"
                line.req_completion_date = fields.Datetime.now()

    # LT Medical Health Insurance Upload end

    @api.onchange('service_request_type')
    def update_service_request_type(self):
        for line in self:
            if line.state == 'draft':
                if line.service_request_type == 'ev_request':
                    line.service_request_config_id = False
                if line.service_request_type == 'lt_request':
                    line.service_request_config_id = False

    
    @api.onchange('employee_id')
    def update_employee_string(self):
        for line in self:
            if line.employee_id:
                line.employee_pay_string = f"{line.employee_id.name}"
                line.sponsor_id = line.employee_id.sponsor_id


    @api.onchange('emp_visa_id')
    def fetch_data_from_transfers(self):
        for line in self:
            line.visa_country_id = line.emp_visa_id.visa_country_id
            line.visa_stamping_city_id = line.emp_visa_id.visa_stamping_city_id
            line.profession = line.emp_visa_id.visa_profession
            line.visa_religion = line.emp_visa_id.visa_religion
            line.no_of_visa = line.emp_visa_id.no_of_visa
            line.agency_allocation = line.emp_visa_id.visa_enjaz
            line.hr_agency = line.emp_visa_id.hr_agency


    def action_confirm(self):
        for line in self:
            line.state = 'done'

    def action_refuse(self):
        for line in self:
            line.state = 'refuse'

    def action_cancel(self):
        for line in self:
            line.state = 'cancel'

    # New Physical Iqama Card Request(cost 1,000sar) start

    # def action_iqama_submit(self):
    #     for line in self:
    #         line.state = 'submitted'
    #         self._add_followers()

    def action_iqama_payment_received_confirmation(self):
        for line in self:
            line.state = 'payment_done'
            line.dynamic_action_status = f"Employee needs to be assigned by PM"

    def action_iqama_process_complete(self):
        for line in self:
            if line.service_request == 'iqama_card_req':
                if line.state == 'payment_done':
                    if line.upload_iqama_card_doc and not line.iqama_card_ref:
                        raise ValidationError("Kindly Update Reference Number for Iqama Card Document")
            line.dynamic_action_status = f"Process Completed"
            line.state = 'done'

    # New Physical Iqama Card Request(cost 1,000sar) end



    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('service.enquiry')
        res = super(ServiceEnquiry,self).create(vals_list)
        # Create the latest existing request name for the alert message visibility,
        if res.service_request_config_id and res.employee_id:
            latest_existing_request = self.search([
                ('employee_id', '=', res.employee_id.id),
                ('service_request_config_id', '=', res.service_request_config_id.id),
                ('id', '!=', res.id)
            ], limit=1)
            if latest_existing_request:
                res.latest_existing_request_id = True
                res.latest_existing_request_name = latest_existing_request.display_name
        return res
    
    @api.onchange('upload_upgrade_insurance_doc','upload_iqama_card_no_doc','upload_iqama_card_doc','upload_qiwa_doc',
        'upload_gosi_doc','upload_hr_card','upload_jawazat_doc','upload_sponsorship_doc','profession_change_doc',
        'upload_payment_doc','profession_change_final_doc','upload_salary_certificate_doc','upload_bank_letter_doc','upload_vehicle_lease_doc',
        'upload_apartment_lease_doc','upload_employment_contract_doc',
        'upload_cultural_letter_doc',
        'upload_emp_secondment_or_cub_contra_ltr_doc','upload_car_loan_doc','upload_rental_agreement_doc',
        'upload_exception_letter_doc','upload_attestation_waiver_letter_doc','upload_embassy_letter_doc','upload_istiqdam_letter_doc',
        'upload_bilingual_salary_certificate_doc','upload_contract_letter_doc','upload_bank_account_opening_letter_doc','upload_bank_limit_upgrading_letter_doc','upload_final_exit_issuance_doc','upload_soa_doc',
        'upload_sec_doc','residance_doc','reupload_hr_card','transfer_confirmation_doc','muqeem_print_doc','upload_issuance_doc','upload_enjaz_doc','e_wakala_doc')
    def document_uploaded(self):
        for line in self:
            if line.upload_upgrade_insurance_doc or line.upload_iqama_card_no_doc or line.upload_iqama_card_doc or line.upload_qiwa_doc or \
            line.upload_gosi_doc or line.upload_hr_card or line.profession_change_doc or line.upload_payment_doc or line.profession_change_final_doc or \
            line.upload_salary_certificate_doc or \
            line.upload_employment_contract_doc or \
            line.upload_bilingual_salary_certificate_doc or  \
            line.upload_final_exit_issuance_doc or line.upload_soa_doc or line.upload_issuance_doc:
                line.doc_uploaded = True
            # elif line.upload_enjaz_doc and line.e_wakala_doc:
            #     line.doc_uploaded = True
            elif line.transfer_confirmation_doc and line.upload_qiwa_doc:
                line.doc_uploaded = True
            elif line.upload_bank_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_vehicle_lease_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_apartment_lease_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_emp_secondment_or_cub_contra_ltr_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_sec_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_rental_agreement_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_istiqdam_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_exception_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_embassy_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_cultural_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_car_loan_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_bank_limit_upgrading_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_bank_account_opening_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            elif line.upload_attestation_waiver_letter_doc and line.fee_receipt_doc:
                line.doc_uploaded = True
            else:
                line.doc_uploaded = False
            if line.upload_jawazat_doc:
                line.second_level_doc_uploaded = True
                
            if line.upload_sponsorship_doc and line.muqeem_print_doc:
                line.final_doc_uploaded = True
            elif line.upload_enjaz_doc and line.e_wakala_doc:
                line.final_doc_uploaded = True
                # above repeated multilpe times
            elif line.residance_doc and line.muqeem_print_doc:
                line.final_doc_uploaded = True
            elif line.reupload_hr_card and line.residance_doc and line.muqeem_print_doc:
                line.final_doc_uploaded = True
            else:
                line.final_doc_uploaded = False

    @api.onchange('service_request')
    def update_doc_updated(self):
        for line in self:
            line.doc_uploaded = False
            self.approver_id = self.client_id.company_spoc_id.id 
            self.approver_user_id = self.approver_id.user_id.id

    
    def _compute_total_treasury_requests(self):
        for line in self:
            employee_id = self.env['service.request.treasury'].search([('service_request_id', '=', line.id)])
            line.total_treasury_requests = len(employee_id)


class ServiceEnquiryPricingLine(models.Model):
    _name = 'service.enquiry.pricing.line'


    service_enquiry_id = fields.Many2one('service.enquiry')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        related="company_id.currency_id",help="The payment's currency.")
    name = fields.Char(string="Description")

    service_pricing_id = fields.Many2one('service.pricing',string="Service Name")
    service_pricing_line_id = fields.Many2one('service.pricing.line',string="Duration")
    amount = fields.Monetary(string="Amount")
    remarks = fields.Text(string="Remarks")