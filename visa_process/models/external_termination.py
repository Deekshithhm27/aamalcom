from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class TerminationService(models.Model):
    _name = "termination.request"
    _description = "Termination Service"
    _inherit = ['mail.thread', 'mail.activity.mixin']
   

    name = fields.Char(string="Reference", copy=False,default=lambda self: self.env['ir.sequence'].next_by_code('termination.request'))

    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('reject', 'Rejected'),
            ('submitted_to_hr', 'Submitted to HR'),
            ('approved_by_pm', 'Reviewed Pending By HR'),
            ('submitted_to_pm', 'Submitted to PM'),
            ('submitted_to_gre', 'Documents Upload Pending '),
            ('approved', 'PM needs to Review'),
            ('done', 'Done'),
        ], string="Status", default="draft", tracking=True)
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    termination_type = fields.Selection([
        ('termination_request', 'Termination'),
    ], string='Service Request',default='termination_request',store=True)
    termination_article_short_version = fields.Selection([
        ('article_53', 'Article 53 - Termination During Probationary Period'),
        ('mutual_agreement', 'Article 74 – Mutual Agreement'),
        ('direct_termination', 'Article 80 – Direct Termination'),
        ('non_renewal', 'Article 74 – Non Renewal'),
        ('retirement_age', 'Article 74 – Retirement Age'),
        ('closure_establishment', 'Article 74 - Closure of the Establishment'),
        ('closure_company_activity', 'Article 74 – Closure of Company’s Activity the Employee is Working in'),
        ('inability_to_work', 'Article 79 - Worker\'s Inability to Work'),
        ('without_legitimate_reason', 'Article 77 – Termination without Legitimate Reasons'),
        ('worker_death', 'Article 79 - Worker\'s Death'),
        ('work_injury', 'Article 137 - Worker\'s Inability to Work (Work Injury)'),
    ], string='Termination Article')
    # Fields to be populated automatically based on the selection
    termination_normal_version = fields.Char(string='Termination Article – Details', compute='_compute_termination_details', store=True)
    notice_period = fields.Char(string='Notice period', compute='_compute_termination_details', store=True)
    immediate_termination = fields.Boolean(string='Immediate Termination', compute='_compute_termination_details', store=True)
    grace_period = fields.Char(string='Grace Period', compute='_compute_termination_details', store=True)
    is_hr_employee = fields.Boolean(
        string="Is HR Employee?",
        compute="_compute_is_hr_employee"
    )
    refuse_reason = fields.Text(string="Refuse Reason", readonly=True,tracking=True)


    @api.depends()
    def _compute_is_hr_employee(self):
        """
        Check if the current user belongs to the HR manager group.
        """
        for rec in self:
            rec.is_hr_employee = self.env.user.has_group('visa_process.group_service_request_hr_employee')

    @api.depends('termination_article_short_version')
    def _compute_termination_details(self):
        for record in self:
            record.termination_normal_version = False
            record.notice_period = False
            record.immediate_termination = False
            record.grace_period = False
            
            if record.termination_article_short_version == 'article_53':
                record.termination_normal_version = 'Direct termination of the contract during the probationary period according to Article 53 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'mutual_agreement':
                record.termination_normal_version = 'By mutual agreement according to Article 74 of the Labor Law'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            # Add more elif conditions for the other options from your table
            elif record.termination_article_short_version == 'direct_termination':
                record.termination_normal_version = 'Direct termination of the employment contract by the employer according to Article 80 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'non_renewal':
                record.termination_normal_version = 'Termination of the contract upon its expiration'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'retirement_age':
                record.termination_normal_version = 'The worker reached retirement age according to Article 74 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'closure_establishment':
                record.termination_normal_version = 'Permanent closure of the establishment according to Article 74 of the Labor Law'
                record.notice_period = 'As per the contract'
                record.immediate_termination = False
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'closure_company_activity':
                record.termination_normal_version = 'Termination of the activity in which the worker is employed according to Article 74 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'inability_to_work':
                record.termination_normal_version = 'Worker\'s inability to work according to Article 79 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'without_legitimate_reason':
                record.termination_normal_version = 'Termination of the contract without a legitimate reason according to Article 77 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
            elif record.termination_article_short_version == 'worker_death':
                record.termination_normal_version = 'Death of the worker according to Article 79 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = 'No'
            elif record.termination_article_short_version == 'work_injury':
                record.termination_normal_version = 'Worker\'s inability to work (resulting from a work injury) according to Article 137 of the Labor Law'
                record.notice_period = 'No'
                record.immediate_termination = True
                record.grace_period = '60 days'
    # New default_get method to pre-fill client fields for specific user groups
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        group_client = self.env.ref('visa_process.group_service_request_client_spoc')
        if group_client in self.env.user.groups_id:
            res['client_id'] = self.env.user.partner_id.id
            res['client_parent_id'] = self.env.user.partner_id.parent_id.id
        return res

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
        required=True
    )
    iqama_no = fields.Char(string="Iqama No", compute="_compute_employee_details", store=True, readonly=True)
    identification_id = fields.Char(string='Border No.', compute="_compute_employee_details", store=True, readonly=True)
    passport_no = fields.Char(string='Passport No', compute="_compute_employee_details", store=True, readonly=True)
    sponsor_id = fields.Many2one('employee.sponsor', string="Sponsor Number", tracking=True)
    load_proof_of_request_doc=fields.Binary(string="Proof of Request Document")
    reason_of_termination=fields.Text(string="Reason of Termination")
    upload_termination_doc = fields.Binary(string="Termination Document")

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            if rec.employee_id:
                rec.iqama_no = rec.employee_id.iqama_no
                rec.sponsor_id = rec.employee_id.sponsor_id.id
                rec.identification_id = rec.employee_id.identification_id
                rec.passport_no = rec.employee_id.passport_id
                rec.sponsor_id = rec.employee_id.sponsor_id
    
    is_project_manager = fields.Boolean(
        compute='_compute_is_project_manager',
        store=False,
        default=False
    )
    def _compute_is_project_manager(self):
        for record in self:
            record.is_project_manager = self.env.user.has_group('visa_process.group_service_request_manager')

    def action_submitted(self):
        for record in self:
            record.state = 'submit'

    def action_submit_to_pm(self):
        for record in self:
            record.state = 'submitted_to_pm'
    
    def action_approved_by_pm(self):
        for record in self:
            record.state = 'approved_by_pm'

    def action_final_review_by_pm(self):
        for record in self:
            record.state = 'approved'
   
   


    def action_process_done(self):
        for record in self:
            record.state = 'done'



