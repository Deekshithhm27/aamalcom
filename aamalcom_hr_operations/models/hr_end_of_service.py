from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EndOfService(models.Model):
    _name = "hr.eos.request"
    _description = "End of Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Sequence for Request ID
    name = fields.Char(
        string='Request ID',
        default=lambda self: self.env['ir.sequence'].next_by_code('hr.eos.request')
    )

    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    # Only Internal Employees will show here
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        domain="[('custom_employee_type', '=', 'internal')]",
      
    )

    employee_user_id = fields.Many2one(
    'res.users',
    string="Employee User",
    related='employee_id.user_id',
    store=True,
    readonly=True   
    )


    # Employee details auto-filled
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)

    upload_eos_doc = fields.Binary(string="EOS Draft Document")
    upload_employee_signed_eos_doc = fields.Binary(string="EOS Document")
    upload_signed_eos_doc = fields.Binary(string="Signed EOS Document")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('reject', 'Rejected'),
        ('submitted_to_payroll', 'Submitted to Payroll'),
        ('approved_by_payroll', 'Approved By Payroll'),
        ('submitted_to_pm', 'Submitted to PM'),
        ('approved_by_pm', 'Approved By PM'),
        ('submitted_to_hr_manager', 'Submitted to HR Manager'),
        ('approved_by_hr_manager', 'Waiting GM Approval'),
        ('submitted_to_gm', 'Submitted to GM'),
        ('approved_by_gm', 'Approved by GM'),
        ('employee_review', 'Pending Employee Review'),
        ('approved_by_employee', 'Confirmed by Employee'),
        ('approved', 'Approved'),
        ('done', 'Done'),
    ], string="Status", default="draft", tracking=True)

    eos_type = fields.Selection([
        ('eos_request', 'End Of Service'),
    ], string='Service Request')

    details_for_eos = fields.Char(string="Details for EOS")
    is_hr_employee = fields.Boolean(
        string="Is HR Employee?",
        compute="_compute_is_hr_employee"
    )

    @api.depends()
    def _compute_is_hr_employee(self):
        """
        Check if the current user belongs to the HR manager group.
        """
        for rec in self:
            rec.is_hr_employee = self.env.user.has_group('visa_process.group_service_request_hr_employee')

    # Default values for Client based on logged-in user group
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
        return res

    # Auto populate details from Employee Master Record
    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
            

    is_current_employee = fields.Boolean(
        string='Is Current Employee',
        compute='_compute_is_current_employee',
        store=False
    )
    
    @api.depends('employee_user_id')
    def _compute_is_current_employee(self):
        """
        Dynamically sets a boolean field to true if the current user
        matches the employee on the record.
        """
        for rec in self:
            rec.is_current_employee = (self.env.user == rec.employee_user_id)
    
    # State Transition Methods
    def action_submit_to_payroll(self):
        if not self.employee_id:
            raise ValidationError("Please select the employee first")
        if not self.eos_type:
            raise ValidationError("Please select the EOS type")
        self.state = 'submitted_to_payroll'
    
    def action_submitted(self):
        self.state = 'submit'


    def action_confirmed_by_payroll(self):
        self.state = 'approved_by_payroll'

    def action_send_to_pm(self):
        self.state = 'submitted_to_pm'

    def action_confirmed_by_pm(self):
        self.state = 'approved_by_pm'

    def action_send_to_hr_manager(self):
        self.state = 'submitted_to_hr_manager'

    def action_confirmed_by_hr_manager(self):
        self.state = 'approved_by_hr_manager'

    def action_send_to_gm(self):
        self.state = 'submitted_to_gm'

    def action_confirmed_by_gm(self):
        self.state = 'approved_by_gm'

    def action_send_to_employee(self):
        self.state = 'employee_review'

    def action_confirmed_by_employee(self):
        self.state = 'approved_by_employee'

    def action_process_done(self):
        self.state = 'done'
