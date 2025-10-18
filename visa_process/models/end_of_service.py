from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class EndOfService(models.Model):
    _name = "eos.request"
    _description = "End of Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Sequence for Request ID
    name = fields.Char(
        string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('eos.request')
    )
    client_id = fields.Many2one('res.partner', string="Client Spoc")
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    client_parent_id = fields.Many2one(
        'res.partner',
        string="Client",
        domain="[('is_company','=',True),('parent_id','=',False)]",
        store=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        store=True
    )
    

    iqama_no = fields.Char(string="Iqama No")
    identification_id = fields.Char(string='Border No.')
    passport_no = fields.Char(string='Passport No')
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('submitted_to_hr', 'Submitted to HR'),
            ('reject', 'Rejected'),
            ('submitted_to_payroll', 'Submitted to Payroll'),
            ('approved_by_payroll', 'Approved By Payroll'),
            ('submitted_to_pm', 'Submitted to PM'),
            ('approved_by_pm', 'Approved By PM'),
            ('submitted_to_hr_manager', 'Submitted to HR Manager'),
            ('approved_by_hr_manager', 'Waiting GM Approval'),
            ('submitted_to_gm', 'Submitted to GM'),
            ('approved_by_gm', 'Approved By GM'),
            ('approved', 'Approved'),
            ('done', 'Done'),
        ], string="Status", default="draft", tracking=True)

    eos_type = fields.Selection([
        ('eos_request', 'End Of Service'),
    ], string='Service Request',default='eos_request', store=True)
    details_for_eos = fields.Text(string="Details for EOS")

    # New default_get method to pre-fill client fields for specific user groups
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
        return res

    
    is_hr_manager = fields.Boolean(
        string="Is HR Manager?",
        compute="_compute_is_hr_manager"
    )

    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)

    upload_eos_doc=fields.Binary(string="EOS Draft Document")

   # Auto populate details from Employee Master Record
    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
       
    @api.depends()
    def _compute_is_hr_manager(self):
        """
        Check if the current user belongs to the HR manager group.
        """
        for rec in self:
            rec.is_hr_manager = self.env.user.has_group('visa_process.group_service_request_hr_employee')


    def action_submit_eos(self):
            """
            Validates required fields and transitions the state from 'draft' to 'submitted_to_hr'.
            """
            for record in self:
                # 1. Validation Checks
                if not record.employee_id:
                    raise ValidationError("Please select the employee first")
                
                # The original validation logic based on the full code snippet
                if not record.eos_type:
                    raise ValidationError("Please select the EOS type")
                
                if not record.details_for_eos:
                    raise ValidationError("Please add Details of EOS")
                
                # 2. State Transition
                record.state = 'submitted_to_hr'
                
                # 3. Optional: Add a message to the chatter
                record.message_post(body="End of Service Request submitted and sent to HR for review.")

    def action_submit_to_payroll(self):
        for record in self:
            record.state = 'submitted_to_payroll'

    def action_confirmed_by_payroll(self):
        for record in self:
            record.state = 'submitted_to_pm'

    def action_send_to_pm(self):
        for record in self:
            record.state = 'submitted_to_pm'

    def action_confirmed_by_pm(self):
        for record in self:
            record.state = 'submitted_to_hr_manager'

    def action_send_to_hr_manager(self):
        for record in self:
            record.state = 'submitted_to_hr_manager'

    def action_confirmed_by_hr_manager(self):
        for record in self:
            record.state = 'approved_by_hr_manager'

    def action_send_to_gm(self):
        for record in self:
            record.state = 'submitted_to_gm'

    def action_confirmed_by_gm(self):
        for record in self:
            record.state = 'approved'

    def action_confirmation_pending_by_pm(self):
        for record in self:
            record.state = 'approved'

    def action_process_done(self):
        for record in self:
            record.state = 'done'




