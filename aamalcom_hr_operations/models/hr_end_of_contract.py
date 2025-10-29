from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class EndofContract(models.Model):
    _name = "hr.end.of.contract"
    _description = "End of Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.end.of.contract'))

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        domain="[('custom_employee_type', '=', 'internal')]",
    )

    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    department_id = fields.Many2one('hr.department', string="Department", compute="_compute_employee_details", store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved_by_dept_head', 'Waiting HR Employee Review'),
        ('submit_to_dept_head', 'Waiting for Approval By Department Head'),
        ('submitted_to_gre', 'Submitted to GRE'),
        ('approved', 'Awaiting HR review'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
    ], string="Status", default="draft")
    contract_end_date = fields.Date(
        string='Contract End Date',
        store=True,
        tracking=True
    )
    notice_period = fields.Date(
        string='Notice Period',
        tracking=True
    )
    upload_notice_period_doc = fields.Binary(string="Notice Period Document")
    final_exit = fields.Boolean(
        string="Final Exit")
    upload_final_exit_doc = fields.Binary(string="Final Exit Document")


    is_my_coach = fields.Boolean(
        string="Is My Coach",
        compute='_compute_is_my_coach',
        store=False
    )
    
    can_submit_end_of_contract = fields.Boolean(
    string="Can Submit",
    compute="_compute_can_submit_end_of_contract",
    store=False
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
            record.message_post(body=_("End of Contract Re-submitted"))

    @api.depends('employee_id')
    def _compute_can_submit_end_of_contract(self):
        for rec in self:
            user = self.env.user
            # Default False
            rec.can_submit_end_of_contract = False  

            # Condition 1: Check if user is the coach of employee
            if rec.employee_id and rec.employee_id.coach_id and user.employee_id == rec.employee_id.coach_id:
                rec.can_submit_end_of_contract = True
                continue  # No need to check groups if already coach

            # Condition 2: Check if user belongs to allowed manager groups
            allowed_groups = [
                'visa_process.group_service_request_hr_manager',
                'visa_process.group_service_request_finance_manager',
                'visa_process.group_service_request_general_manager',
                'visa_process.group_service_request_operations_manager',
                'visa_process.group_service_request_govt_manager',
            ]
            if any(user.has_group(group) for group in allowed_groups):
                rec.can_submit_end_of_contract = True

    
   
    @api.depends('employee_id')
    def _compute_is_my_coach(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.coach_id:
                current_user_employee = self.env.user.employee_id
                rec.is_my_coach = (current_user_employee == rec.employee_id.coach_id)
            else:
                rec.is_my_coach = False
     

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
                rec.department_id = rec.employee_id.department_id.id
                rec.sponsor_id = rec.employee_id.sponsor_id
    
    def action_submit_by_dept_head(self):
        self.state = 'approved_by_dept_head'
        return True 

    def action_submit_end_of_contract(self):
        self.state = 'submit_to_dept_head'
        return True 
    
    def action_approve_by_dept_head(self):
        self.state = 'approved_by_dept_head'
        return True 

    def action_process_complete_end_of_contract(self):
        for rec in self:
            # Validation: check notice period and document
            if not rec.notice_period:
                raise ValidationError(_("Please set the Notice Period before completing the process."))

            if not rec.upload_notice_period_doc:
                raise ValidationError(_("Please upload the Notice Period document before completing the process."))

            # If all validations pass, mark as done
            rec.state = 'done'
            rec.message_post(body=_("End of Contract process completed successfully."))
        return True

