# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HRMedicalBloodTest(models.Model):
    _name = "hr.medical.blood.test"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"
    _description ="Iqama Issuance-Medical Blood Test"

    service_type = fields.Selection([
        ('iqama_issuance', 'Iqama Issuance - Medical Blood Test'),
    ], string="Service Request", default='iqama_issuance')

    name = fields.Char(string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.medical.blood.test'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        domain="[('custom_employee_type', '=', 'internal')]",
    )
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    upload_stamped_visa_doc = fields.Binary(string="Stamped Visa Document")
    stamped_visa_doc_ref = fields.Char(string="Ref No.*")
    upload_stamped_visa_doc_file_name = fields.Char(string="Stamped Visa Document")
    upload_medical_test_doc = fields.Binary(string="Medical Test Document")
    medical_test_doc_ref = fields.Char(string="Ref No.*")
    upload_medical_test_doc_file_name = fields.Char(string="Medical Test Document")
    clinic_name = fields.Char(string="Clinic Name")
    total_amount = fields.Monetary(string="Amount")

    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )

    total_price = fields.Monetary(string="Price")
    
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved_by_dept_head', 'Waiting for HR Manager Approval'),
        ('passed_to_treasury', 'Passed to Treasury'),
        ('submit_to_fm', 'Waiting for FM Approval'),
        ('submit_to_gm', 'Waiting for GM Approval'),
        ('submit_to_treasury', 'Waiting for Treasury Approval'),
        ('submit_for_approval', 'Waiting OH Approval'),
        ('approved', 'Approved'),
        ('submitted_to_gre', 'Submitted to GRE'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
    ], string="Status", default="draft")
    treasury_confirmation_doc = fields.Binary(
        string="Payment Confirmation Doc",
        copy=False,
        attachment=True,
    )
    treasury_confirmation_ref = fields.Char(
        string="Ref No.",
        copy=False,
    )

    is_gov_employee = fields.Boolean(compute='_compute_is_gov_employee', store=False)
    @api.depends('is_gov_employee')
    def _compute_is_gov_employee(self):
        for record in self:
            record.is_gov_employee = self.env.user.has_group('visa_process.group_service_request_employee')

    is_project_manager = fields.Boolean(
        compute='_compute_is_project_manager',
        store=False,
        default=False
    )
    def _compute_is_project_manager(self):
        for record in self:
            record.is_project_manager = self.env.user.has_group('visa_process.group_service_request_manager')

    confirmation_doc = fields.Binary(string="Confirmation Doc*")
    confirmation_doc_filename = fields.Char(string="Conformation Document")
    confirmation_doc_ref = fields.Char(string="Ref No.*")

    treasury_request_ids = fields.One2many(
        'hr.service.request.treasury',
        'service_request_ref',
        string="Treasury Requests"
    )

    total_treasury_requests = fields.Integer(
        string="Treasury Requests",
        compute="_compute_total_treasury_requests"
    )
    reject_reason = fields.Text('Reason for Rejection', readonly=True, copy=False)
    def action_reject(self):
            for rec in self:
                if rec.state == 'draft':
                    raise UserError(_("requests in draft state cant be rejected."))
            return {
                'name': 'Reject Change Request',
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee.change.request.reject.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'active_ids': self.ids},
            }
    def action_resubmit(self):
        for record in self:
            record.state = 'draft'
            record.message_post(body=_("AnnualRequestService Re-submitted ."))

    
    def _compute_total_treasury_requests(self):
        for rec in self:
            rec.total_treasury_requests = self.env['hr.service.request.treasury'].search_count(
                [('service_request_ref', '=', f'hr.medical.blood.test,{rec.id}')]
            )

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
            
    def action_submit_medical(self):
        self.ensure_one()
        self.state = 'submitted'
        return True

    def action_submit_to_treasury_hr(self):
        self.ensure_one()
        self.state = 'passed_to_treasury'
        treasury_record_vals = {
            'service_request_ref': f'hr.medical.blood.test,{self.id}',
            'employee_id': self.employee_id.id,
            'total_amount': self.total_price,
            'clinic_name': self.clinic_name,
            'state': 'passed_to_treasury',
            'service_type': self.service_type,
        }
        self.env['hr.service.request.treasury'].create(treasury_record_vals)
        self.message_post(body=_("Request submitted to Treasury by HR."))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_view_treasury_requests(self):
        self.ensure_one()
        self.message_post(body=_("Viewed Treasury Requests."))
        return {
            'name': _('Treasury Requests'),
            'view_mode': 'tree,form',
            'res_model': 'hr.service.request.treasury',
            'type': 'ir.actions.act_window',
            'domain': [('service_request_ref', '=', f'hr.medical.blood.test,{self.id}')],
            'context': {'create': False}
        }

    def action_oh_approve(self):
        for record in self:
            record.state = 'submit_to_gm'
            record.message_post(body=_("Approved by OH and forwarded to GM."))

    def action_gm_approve(self):
        for record in self:
            record.state = 'submit_to_fm'
            record.message_post(body=_("Approved by GM and forwarded to FM."))

    def action_fm_approve(self):
        for record in self:
            treasury_record = self.env['hr.service.request.treasury'].search([
                ('service_request_ref', '=', f'hr.medical.blood.test,{record.id}')
            ], limit=1)
            if treasury_record:
                treasury_record.write({'state': 'submitted'})
                record.state = 'submit_to_treasury'
                record.message_post(body=_("FM approved and Treasury Request updated to 'Submitted'."))
            else:
                record.state = 'submit_to_treasury'
                record.message_post(body=_("FM approved. Treasury Request not found, waiting for creation."))
        return True

    def action_process_complete(self):
        for record in self:
            if record.upload_medical_test_doc and not record.medical_test_doc_ref:
                raise ValidationError("Kindly Update Reference Number for Medical Test Doc")
            record.state = 'done'
            record.message_post(body=_("Medical Process Completed."))
