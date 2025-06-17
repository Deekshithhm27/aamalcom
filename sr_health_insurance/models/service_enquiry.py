from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('health_insurance', 'Health Insurance -Enrollment on Border Number'),
            ('enrollment_for_work_visa', 'Enrollment for Work Visit Visa')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'health_insurance': 'cascade','enrollment_for_work_visa':'cascade'}
    )

    enrollment_health = fields.Selection([('employment_visa', 'Employment Visa'),('dependent_visa', 'Dependent Visa')], string="Enrollment on Border Number", store=True)
    insurance_class = fields.Selection([('vip_plus', 'VIP+'),('vip', 'VIP'),('a_plus', 'A+'),('a', 'A'),('b_plus', 'B+'),('b', 'B'),('c_plus', 'C+'),('c', 'C'),('d_plus', 'D+'),('d', 'D'),('e_plus', 'E+'),('e', 'E')], string="Class of Insurance", store=True)
    is_inside_ksa = fields.Boolean(string="Inside KSA")
    is_outside_ksa = fields.Boolean(string="Outside KSA")
    membership_no=fields.Char(string="membership Number")
    upload_hdf_doc=fields.Binary(string="Upload Pre-filled HDF Document")
    upload_hdf_doc_file_name=fields.Char(string="HDF Document")
    hdf_doc_ref=fields.Char(string="Ref No.*")
    upload_passport_doc=fields.Binary(string="Upload Passport Document")
    upload_passport_doc_file_name=fields.Char(string="Passport Document")
    passport_doc_ref=fields.Char(string="Ref No.*")
    upload_issued_visa_doc=fields.Binary(string="Upload Issued Visa Document")
    upload_issued_visa_doc_file_name=fields.Char(string="Issued Visa Document")
    issued_visa_doc_ref=fields.Char(string="Ref No.*")
    upload_cchi_doc=fields.Binary(string="Upload CCHI Confiramtion Document")
    upload_cchi_doc_file_name=fields.Char(string="Issued Visa Document")
    cchi_doc_ref=fields.Char(string="Ref No.*")
    upload_birth_doc=fields.Binary(string="Upload Birth Certificate Document")
    upload_birth_doc_file_name=fields.Char(string="Birth Document")
    birth_doc_ref=fields.Char(string="Ref No.*")


    @api.onchange('is_inside_ksa')
    def _onchange_is_inside_ksa(self):
        if self.is_inside_ksa:
            self.is_outside_ksa = False

    @api.onchange('is_outside_ksa')
    def _onchange_is_outside_ksa(self):
        if self.is_outside_ksa:
            self.is_inside_ksa = False

    def action_submit(self):
        """Validation checks before submitting the service request."""
        super(ServiceEnquiry, self).action_submit()
        for line in self:
            if line.service_request == 'health_insurance':
                if not line.enrollment_health:
                    raise ValidationError("Please select at least one: Either Employment Visa or Dependent Visa.")
                line.dynamic_action_status = f"Documents Need to be uploaded by Insurance Dept"
                line.state='submitted_to_insurance'
            if line.service_request == 'enrollment_for_work_visa':
                line.dynamic_action_status = f"Documents Need to be uploaded by Insurance Dept"
                line.state='submitted_to_insurance'

    def action_submit_enrollment(self):
        for line in self:
            if line.service_request == 'health_insurance':
                if line.upload_hdf_doc and not line.hdf_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for HDF form")
                if line.upload_passport_doc and not line.passport_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Passport Document")
                if line.upload_issued_visa_doc and not line.issued_visa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Issued Visa Document")
                if line.upload_cchi_doc and not line.cchi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for CCHI Document")
                if line.upload_birth_doc and not line.birth_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Birth Document")
                line.dynamic_action_status=f"Documents Uploaded by Insurance Department, Pm needs to close the ticket"
                line.state='submit_to_pm'
            if line.service_request == 'enrollment_for_work_visa':
                if line.upload_hdf_doc and not line.hdf_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for HDF form")
                if line.upload_passport_doc and not line.passport_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Passport Document")
                if line.upload_issued_visa_doc and not line.issued_visa_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Issued Visa Document")
                if line.upload_cchi_doc and not line.cchi_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for CCHI Document")
                if line.upload_birth_doc and not line.birth_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Birth Document")
                line.dynamic_action_status=f"Documents Uploaded by Insurance Department, Pm needs to close the ticket"
                line.state='submit_to_pm'

    def action_process_complete_enrollment(self):
        for line in self:
            if line.service_request == 'health_insurance':
                line.dynamic_action_status=f"Process Completed"
                line.action_user_id=False
                line.state='done'
            if line.service_request == 'enrollment_for_work_visa':
                line.dynamic_action_status=f"Process Completed"
                line.action_user_id=False
                line.state='done'


                