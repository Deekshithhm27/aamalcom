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
    _inherit = ['mail.thread']
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
        ('waiting_op_approval','Waiting OH Approval'),
        ('waiting_gm_approval','Waiting GM Approval'),
        ('waiting_fin_approval','Waiting FM Approval'),
        ('approved','Approved'),
        ('payment_initiation','Payment Initiation'),
        ('payment_done','Payment Confirmation'),
        ('done', 'Done'),('refuse','Refuse'),('cancel','Cancel')], string='State',default="draft",copy=False,tracking=True)
    service_request_type = fields.Selection([('lt_request','Local Transfer'),('ev_request','Employment Visa')],string="Service Request Type",tracking=True,copy=False)
    service_request_config_id = fields.Many2one('service.request.config',string="Service Request",domain="[('service_request_type','=',service_request_type)]",copy=False)
    process_type = fields.Selection([('automatic','Automatic'),('manual','Manual')],string="Process Type",default="manual",copy=False)


    @api.onchange('service_request_config_id')
    def update_process_type(self):
        for line in self:
            if line.service_request_config_id:
                line.process_type = line.service_request_config_id.process_type

    service_request = fields.Selection([('new_ev','Issuance of New EV'),
        ('sec','SEC Letter'),('hr_card','Issuance for HR card'),('transfer_req','Transfer Request Initiation'),
        ('ins_class_upgrade','Medical health insurance Class Upgrade'),
        ('iqama_no_generation','Iqama No generation'),('iqama_card_req','New Physical Iqama Card Request'),
        ('qiwa','Qiwa Contract'),('gosi','GOSI Update'),('iqama_renewal','Iqama Renewal'),('exit_reentry_issuance','Exit Rentry issuance'),
        ('prof_change_qiwa','Profession change Request In qiwa'),('salary_certificate','Salary certificate'),
        ('bank_letter','Bank letter'),('vehicle_lease','Letter for Vehicle Lease'),
        ('apartment_lease','Letter for Apartment Lease'),('istiqdam_form','Istiqdam Form(Family Visa Letter)'),
        ('family_visa_letter','Family Visa Letter'),('employment_contract','Employment contract'),
        ('cultural_letter','Cultural Letter/Bonafide Letter'),
        ('family_visit_visa','Family Visit Visa'),
        ('emp_secondment_or_cub_contra_ltr','Employee secondment / Subcontract letter'),
        ('car_loan','Car Loan Letter'),('bank_loan','Bank Loan Letter'),('rental_agreement','Rental Agreement Letter'),
        ('exception_letter','Exception Letter'),('attestation_waiver_letter','Attestation Waiver Letter'),
        ('embassy_letter','Embassy Letters- as Per Respective Embassy requirement'),('istiqdam_letter','Istiqdam Letter'),
        ('sce_letter','SCE Letter'),('bilingual_salary_certificate','Bilingual Salary Certificate'),('contract_letter','Contract Letter'),
        ('bank_account_opening_letter','Bank account Opening Letter'),('bank_limit_upgrading_letter','Bank Limit upgrading Letter'),
        ('final_exit_issuance','Final exit Issuance'),
        ('dependent_transfer_query','Dependent Transfer Query'),('soa','Statement of account till date'),('general_query','General Query')],string="Service Requests",related="service_request_config_id.service_request",store=True,copy=False)
    
    employee_id = fields.Many2one('hr.employee',domain="[('custom_employee_type', '=', 'external'),('client_id','=',user_id)]",string="Employee",store=True,tracking=True,required=True,copy=False)

    transfer_type = fields.Selection([('to_aamalcom','To Aamalcom'),('to_another_establishment','To another Establishment')],string="Transfer Type")
    transfer_amount = fields.Float(string="Amount")

    is_penalty_applicable = fields.Boolean(string="Is Penalty Applicable?",copy=False)
    penalty_cost = fields.Float(string="Penalty Cost",copy=False)
    


    @api.onchange('employee_id')
    def update_service_request_type_from_employee(self):
        for line in self:
            if line.employee_id:
                line.service_request_type = line.employee_id.service_request_type
    
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
    hr_card_ref = fields.Char(string="Ref No.")
    upload_jawazat_doc = fields.Binary(string="Jawazat Document")
    jawazat_doc_ref = fields.Char(string="Ref No.")
    upload_payment_doc = fields.Binary(string="Payment Confirmation Document",tracking=True)
    payment_doc_ref = fields.Binary(string="Ref No.")
    residance_doc = fields.Binary(string="Residance Permit Document")
    residance_doc_ref = fields.Char(string="Ref No.")
    transfer_confirmation_doc = fields.Binary(string="Confirmation of Transfer")
    transfer_confirmation_ref = fields.Binary(string="Ref No.")
    muqeem_print_doc = fields.Binary(string="Muqeem Print Document")
    muqeem_print_doc_ref = fields.Char(string="Ref No.")

    upload_upgrade_insurance_doc = fields.Binary(string="Confirmation of Insurance upgarde Document")
    upgarde_ins_doc_ref = fields.Char(string="Ref No.")

    request_date = fields.Datetime(string="Request Date",default=fields.Datetime.now)

    upload_iqama_card_doc = fields.Binary(string="Upload Iqama Card")
    iqama_card_ref = fields.Char(string="Ref No.")
    upload_iqama_card_no_doc = fields.Binary(string="Upload Iqama Card")
    iqama_card_no_ref = fields.Char(string="Ref No.")
    upload_qiwa_doc = fields.Binary(string="Upload Qiwa Contract")
    qiwa_doc_ref = fields.Char(string="Ref No.")
    upload_gosi_doc = fields.Binary(string="Upload GOSI Update")
    gosi_doc_ref = fields.Char(string="Ref No.")
    profession_change_doc = fields.Binary(string="Profession Change Req. Doc")
    profession_change_doc_ref = fields.Char(string="Ref No.")
    profession_change_final_doc = fields.Binary(string="Profession Change Req. Doc")
    prof_change_final_ref = fields.Char(string="Ref No.")
    upload_salary_certificate_doc = fields.Binary(string="Salary Certificate")
    salary_certificate_ref = fields.Char(string="Ref No.")
    upload_bank_letter_doc = fields.Binary(string="Bank Letter")
    bank_letter_ref = fields.Char(string="Ref No.")
    upload_vehicle_lease_doc = fields.Binary(string="Letter for Vehicle lease")
    vehicle_lease_ref = fields.Char(string="Ref No.")
    upload_apartment_lease_doc = fields.Binary(string="Letter for Apartment lease")
    apartment_lease_ref = fields.Char(string="Ref No.")
    upload_family_visa_letter_doc = fields.Binary(string="Family Visa Letter")
    family_visa_letter_doc_ref = fields.Char(string="Ref No.")
    upload_visit_visa_app_doc = fields.Binary(string="Upload Visit Visa application")
    visit_visa_app_doc_ref = fields.Char(string="Ref No.")
    upload_family_visit_visa_doc = fields.Binary(string="Family Visit Visa Doc")
    family_visit_visa_doc_ref = fields.Char(string="Ref No.")
    upload_employment_contract_doc = fields.Binary(string="Employment Contract")
    employment_contract_doc_ref = fields.Char(string="Ref No.")
    upload_cultural_letter_doc = fields.Binary(string="Cultural Letter")
    cultural_letter_doc_ref = fields.Char(string="Ref No.")
    draft_istiqdam = fields.Binary(string="Draft Istiqdam",compute="auto_fill_istiqdam_form",store=True)
    updated_istiqdam_form_doc = fields.Binary(string="Updated Istiqdam Form")
    upload_istiqdam_form_doc = fields.Binary(string="Upload Istiqdam Form")
    istiqdam_form_doc_ref = fields.Char(string="Ref No.")
    upload_confirmation_of_exit_reentry = fields.Binary(string="Upload Confirmation of Exit re-entry")
    confirmation_of_exit_reentry_ref = fields.Char(string="Ref No.")
    upload_exit_reentry_visa = fields.Binary(string="Exit Re-entry Visa")
    exit_reentry_visa_ref = fields.Char(string="Ref No.")
    upload_final_exit_issuance_doc = fields.Binary(string="Final Exit issuance doc")
    final_exit_issuance_doc_ref = fields.Char(string="Ref No.")
    upload_soa_doc = fields.Binary(string="SOA Doc")
    soa_doc_ref = fields.Char(string="Ref No.")
    upload_emp_secondment_or_cub_contra_ltr_doc = fields.Binary(string="Employee secondment / Subcontract Document")
    emp_secondment_ltr_doc_ref = fields.Char(string="Ref No.")
    upload_car_loan_doc = fields.Binary(string="Car Loan Document")
    car_loan_doc_ref = fields.Char(string="Ref No.")
    upload_bank_loan_doc = fields.Binary(string="Bank Loan Document")
    bank_loan_doc_ref = fields.Char(string="Ref No.")
    upload_rental_agreement_doc = fields.Binary(string="Rental Agreement Document")
    rental_agreement_doc_ref = fields.Char(string="Ref No.")
    upload_exception_letter_doc = fields.Binary(string="Exception Document")
    exception_letter_doc_ref = fields.Char(string="Ref No.")
    upload_attestation_waiver_letter_doc = fields.Binary(string="Attestation Waiver Document")
    attestation_waiver_letter_doc_ref = fields.Char(string="Ref No.")
    upload_embassy_letter_doc = fields.Binary(string="Embassy Letter")
    embassy_letter_doc_ref = fields.Char(string="Ref No.")
    upload_istiqdam_letter_doc = fields.Binary(string="Istiqdam Letter")
    istiqdam_letter_doc_ref = fields.Char(string="Ref No.")
    # upload_sce_letter_doc = fields.Binary(string="SCE Letter")
    upload_bilingual_salary_certificate_doc = fields.Binary(string="Bilingual Salary Certificate")
    bilingual_salary_certificate_doc_ref = fields.Char(string="Ref No.")
    upload_contract_letter_doc = fields.Binary(string="Contract Letter")
    contract_letter_doc_ref = fields.Char(string="Ref No.")
    upload_bank_account_opening_letter_doc = fields.Binary(string="Bank account Opening Letter")
    bank_account_opening_letter_doc_ref = fields.Char(string="Ref No.")
    upload_bank_limit_upgrading_letter_doc = fields.Binary(string="Bank Limit upgrading Letter")
    bank_limit_upgrading_letter_doc_ref = fields.Char(string="Ref No.")

    
    reason_for_loss_of_iqama = fields.Text(string="Reason for loss of Iqama")
    letter_from_police_station = fields.Binary(string="Letter from the police station of the lost iqama")
    note = fields.Text(string="Note",default="Note: Cost 1000 sar, invoice not available")
    visit_visa_note = fields.Text(string="Note",default="Note: Document will be Attested by COC ")
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")


    # EV Fields

    visa_country_id = fields.Many2one('res.country',string="Visa issuing country")
    visa_state_id = fields.Char(string="Visa issuing city")
    visa_religion = fields.Selection([('muslim','Muslim'),('non_muslim','Non-Muslim'),('others','Others')],string="Visa Religion")
    no_of_visa = fields.Integer(string="No of Visa")
    profession = fields.Char(string="Profession",tracking=True)
    agency_allocation = fields.Text(string="Allocation of Agency (E wakala)")
    coc_for_ewakala = fields.Boolean(string="COC for Ewakala",compute="update_coc_for_ewakala",store=True)

    upload_issuance_doc = fields.Binary(string="Upload Issuance of Visa Document")
    issuance_doc_ref = fields.Char(string="Ref No.")
    upload_enjaz_doc = fields.Binary(string="Enjaz Document")
    enjaz_doc_ref = fields.Char(string="Ref No.")
    upload_sec_doc = fields.Binary(string="SEC Letter")
    sec_doc_ref = fields.Char(string="Ref No.")

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
    exit_type = fields.Selection([('single','Single'),('multiple','Multiple')],string="Type")

    
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
            
    to_be_issued_date = fields.Date(string="To be issued from")

    current_insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Current Insurance Class")
    class_to_be_changed = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Class to be changed to!")
    duration_limit = fields.Selection([('30','30'),('60','60'),('90','90'),('120','120'),('150','150'),('180','180'),('210','210'),('240','240'),('270','270'),('300','300'),('330','330'),('360','360')],string="Duration")


    insurance_class = fields.Selection([('class_vip+','VIP+'),('class_vip','VIP'),('class_a','A'),('class_b','B'),('class_c','C'),('class_e','E')],string="Current Insurance Class")

    document_upload = fields.Binary(string="Document Upload")
    logical_reason = fields.Text(string="Logical Reason to be stated")
    border_id_doc = fields.Binary(string="Upload Iqama /Passport with border ID")
    # cost_to_be_borne_by = fields.Selection([('aamalcom','Aamalcom'),('client','Client')],string="Cost To be borne by")
    iqama_upload = fields.Binary(string="Iqama Upload")
    profession_change = fields.Char(string="Profession change to")
    soa_date = fields.Date(string="Duration")
    duration = fields.Char(string="Duration")


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
    final_doc_uploaded = fields.Boolean(string="Final Document uploaded",default=False,copy=False)
    total_treasury_requests = fields.Integer(string="Request Details",compute="_compute_total_treasury_requests")

    is_service_request_client_spoc = fields.Boolean(
        string="Is Service Request Client SPOC",
        compute='_compute_is_service_request_client_spoc'
    )

    @api.depends('user_id.groups_id')
    def _compute_is_service_request_client_spoc(self):
        """Compute function to check if the user belongs to group_service_request_client_spoc"""
        spoc_group = self.env.ref('visa_process.group_service_request_client_spoc')
        for record in self:
            record.is_service_request_client_spoc = spoc_group in record.env.user.groups_id

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

    @api.depends('state','service_request_config_id')
    def update_departments(self):
        # this method fetches departments configured in service request based on hierarchy
        for line in self:
            department_ids = []
            if line.service_request_config_id.service_department_lines:
                if not line.service_request_config_id.service_request == 'iqama_card_req':
                    line.current_department_ids = False
                    for lines in line.service_request_config_id.service_department_lines:
                        if line.state in ('submitted','waiting_gm_approval','waiting_op_approval','waiting_fin_approval'):
                            if lines.sequence == 1:
                                # line.current_department_id = lines.department_id.id
                                department_ids.append((4,lines.department_id.id))
                                line.current_department_ids = department_ids
                                break
                            else:
                                line.current_department_ids = False
                        elif line.state in ('payment_done','approved'):
                            if lines.sequence == 2:
                                # line.current_department_id = lines.department_id.id
                                department_ids.append((4,lines.department_id.id))
                                line.current_department_ids = department_ids
                                break
                            else:
                                line.current_department_ids = False
                        else:
                            line.current_department_ids = False
                else:
                    
                    for lines in line.service_request_config_id.service_department_lines:
                        department_ids.append((4,lines.department_id.id))
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

            department_ids = [(6, 0, self.current_department_ids.ids)]

            return {
                'name': 'Select Employee',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_department_ids': department_ids},
            }

    def open_reassign_employee_wizard(self):
        department_ids = [(6, 0, self.current_department_ids.ids)]
        return {
                'name': 'Select Employee',
                'type': 'ir.actions.act_window',
                'res_model': 'employee.selection.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_department_ids': department_ids},
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




    def update_pricing(self):
        for record in self:
            record.service_enquiry_pricing_ids = False
            pricing_id = self.env['service.pricing'].search([('service_request_type', '=', record.service_request_type),
                    ('service_request', '=', record.service_request)], limit=1)
            print("----priceing",pricing_id)
            if record.aamalcom_pay and record.service_request != 'transfer_req':
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
                record.service_enquiry_pricing_ids.create({
                    'name':"Letter Cost",
                    'amount':record.letter_cost,
                    'service_enquiry_id':record.id,
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
            line.state = 'submitted'
            line.doc_uploaded = False
            if line.service_request:
                line.assign_govt_emp_one = True
            self.update_pricing()
            self._add_followers()

    def action_require_payment_confirmation(self):
        for line in self:
            line.state = 'payment_initiation'
            line.doc_uploaded = False
    def action_submit_for_approval(self):
        for line in self:
            line.state = 'waiting_op_approval'
    def action_op_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]

        for line in self:
            line.state = 'waiting_gm_approval'
            line.op_approver_id = current_employee
    def action_gm_approved(self):
        current_employee = self.env.user.employee_ids and self.env.user.employee_ids[0]
        for line in self:
            line.state = 'waiting_fin_approval'
            line.gm_approver_id = current_employee

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
                if line.service_request == 'hr_card' or line.service_request == 'iqama_renewal' or line.service_request == 'transfer_req' or line.service_request == 'new_ev':
                    line.assign_govt_emp_two = True


    def action_submit_payment_confirmation(self):
        for line in self:
            line.state = 'payment_done'
            line.doc_uploaded = False
            if line.service_request == 'hr_card' or line.service_request == 'iqama_renewal':
                line.assign_govt_emp_two = True
            if line.service_request == 'prof_change_qiwa' or line.service_request == 'new_ev':
                line.doc_uploaded = True

    

    # LT Issuance of HR Card and Iqama Renewal end



    # LT Medical Health Insurance Upload start

    def action_submit_initiate(self):
        for line in self:
            line.state = 'submitted'
            if line.service_request:
                line.assign_govt_emp_one = True
            self.update_pricing()
            self._add_followers()

    def action_process_complete(self):
        for line in self:
            if line.service_request == 'prof_change_qiwa':
                treasury_id = self.env['service.request.treasury'].search([('service_request_id','=',line.id)])
                if treasury_id:
                    for srt in treasury_id:
                        if srt.state != 'done':
                            raise ValidationError(_('Action required by Finance team. Kindly upload Confirmation Document provided by Treasury Department before continuing further'))
                else:
                    line.state = 'done'
                    line.req_completion_date = fields.Datetime.now()


            else:
                line.state = 'done'
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

    @api.depends('service_request')
    def auto_fill_istiqdam_form(self):
        for line in self:
            if line.service_request == 'istiqdam_form':
                istiqdam_id = self.env['visa.ref.documents'].search([('is_istiqdam_doc','=',True)],limit=1)
                line.draft_istiqdam = istiqdam_id.istiqdam_doc
            else:
                line.draft_istiqdam = False
    @api.onchange('employee_id')
    def update_employee_string(self):
        for line in self:
            if line.employee_id:
                line.employee_pay_string = f"{line.employee_id.name}"

    @api.onchange('emp_visa_id')
    def fetch_data_from_transfers(self):
        for line in self:
            line.visa_country_id = line.emp_visa_id.visa_country_id
            line.visa_stamping_city_id = line.emp_visa_id.visa_stamping_city_id
            line.profession = line.emp_visa_id.visa_profession
            line.visa_religion = line.emp_visa_id.visa_religion
            line.no_of_visa = line.emp_visa_id.no_of_visa
            line.agency_allocation = line.emp_visa_id.visa_enjaz


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

    def action_iqama_process_complete(self):
        for line in self:
            line.state = 'done'

    # New Physical Iqama Card Request(cost 1,000sar) end

 
    # Issuance of New EV start
    def action_submit_new_ev(self):
        for line in self:
            line.state = 'submitted'

    def action_new_ev_process_complete(self):
        for line in self:
            line.state='done'

    # Issuance of New EV end



    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('service.enquiry')
        res = super(ServiceEnquiry,self).create(vals_list)
        return res

    def _add_followers(self):
        """
            Add Approver as followers
        """
        partner_ids = []
        if self.approver_id:
            partner_ids.append(self.approver_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)


    
    @api.onchange('upload_upgrade_insurance_doc','upload_iqama_card_no_doc','upload_iqama_card_doc','upload_qiwa_doc',
        'upload_gosi_doc','upload_hr_card','upload_jawazat_doc','upload_confirmation_of_exit_reentry','upload_exit_reentry_visa','profession_change_doc',
        'upload_payment_doc','profession_change_final_doc','upload_salary_certificate_doc','upload_bank_letter_doc','upload_vehicle_lease_doc',
        'upload_apartment_lease_doc','upload_istiqdam_form_doc','upload_family_visa_letter_doc','upload_employment_contract_doc',
        'upload_cultural_letter_doc','upload_family_visit_visa_doc',
        'upload_emp_secondment_or_cub_contra_ltr_doc','upload_car_loan_doc','upload_bank_loan_doc','upload_rental_agreement_doc',
        'upload_exception_letter_doc','upload_attestation_waiver_letter_doc','upload_embassy_letter_doc','upload_istiqdam_letter_doc',
        'upload_bilingual_salary_certificate_doc','upload_contract_letter_doc','upload_bank_account_opening_letter_doc','upload_bank_limit_upgrading_letter_doc','upload_final_exit_issuance_doc','upload_soa_doc',
        'upload_sec_doc','residance_doc','transfer_confirmation_doc','muqeem_print_doc','upload_issuance_doc','upload_enjaz_doc')
    def document_uploaded(self):
        for line in self:
            if line.upload_upgrade_insurance_doc or line.upload_iqama_card_no_doc or line.upload_iqama_card_doc or line.upload_qiwa_doc or \
            line.upload_gosi_doc or line.upload_hr_card or line.upload_jawazat_doc or line.profession_change_doc or line.upload_payment_doc or line.profession_change_final_doc or \
            line.upload_salary_certificate_doc or line.upload_bank_letter_doc or line.upload_vehicle_lease_doc or line.upload_apartment_lease_doc or \
            line.upload_istiqdam_form_doc or line.upload_family_visa_letter_doc or line.upload_employment_contract_doc or line.upload_cultural_letter_doc or \
            line.upload_family_visit_visa_doc or \
            line.upload_emp_secondment_or_cub_contra_ltr_doc or line.upload_car_loan_doc or line.upload_bank_loan_doc or line.upload_rental_agreement_doc or \
            line.upload_exception_letter_doc or line.upload_attestation_waiver_letter_doc or line.upload_embassy_letter_doc or line.upload_istiqdam_letter_doc or \
            line.upload_bilingual_salary_certificate_doc or line.upload_contract_letter_doc or line.upload_bank_account_opening_letter_doc or line.upload_bank_limit_upgrading_letter_doc or \
            line.upload_final_exit_issuance_doc or line.upload_soa_doc or line.upload_sec_doc:
                line.doc_uploaded = True
            elif line.upload_confirmation_of_exit_reentry and line.upload_exit_reentry_visa:
                line.doc_uploaded = True
            elif line.upload_enjaz_doc and line.upload_issuance_doc:
                line.doc_uploaded = True
            else:
                line.doc_uploaded = False
                
            if (line.residance_doc or line.transfer_confirmation_doc) and line.muqeem_print_doc:
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