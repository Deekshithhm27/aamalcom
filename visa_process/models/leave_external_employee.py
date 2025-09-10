# models/visa_leave.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class VisaLeave(models.Model):
    _name = "visa.leave"
    _description = "Employee Leave"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        
    )
   

    state = fields.Selection([
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('reject', 'Rejected'),
            ('submitted_to_gre', 'Submitted to GRE'),
            ('done', 'Done'),
        ], string="Status", default="draft", tracking=True)

    leave_type = fields.Selection([
        ('annual', 'Annual Vacation'),
        ('sick', 'Sick Leave'),
        ('injury', 'Work Injury'),
        ('wfh', 'Work From Home'),
        ('eid', 'Eid Holidays'),
        ('emergency', 'Emergency Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('hajj', 'Hajj Vacation'),
        ('married', 'Married Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ], string="Type of Leave", required=True)

   
    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    number_of_days = fields.Integer(string="Number of Days", compute="_compute_days", store=True)

    upload_medical_report_doc = fields.Binary(string="Medical Report")
    medical_report_filename = fields.Char(string="Medical Report Filename")

    upload_accident_report_doc = fields.Binary(string="Accident Report")
    accident_report_filename = fields.Char(string="Accident Report Filename")
    upload_snapshot_doc = fields.Binary(string="Documents")
    ref_no_snapshot = fields.Char(string="Ref No.*")

    is_gre = fields.Boolean(
        string="Is Govt Employee?",
        compute="_compute_is_gre"
    )
    religion = fields.Selection([
            ('muslim', 'Muslim'),
            ('non_muslim', 'Non-Muslim'),
            ('others', 'Others') 
        ], string="Religion")

       
    """
    Fetches the religion from the linked employee record.
    """    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.religion = self.employee_id.religion

   
            
           

    @api.depends()
    def _compute_is_gre(self):
        """
        Check if the current user belongs to the HR manager group.
        """
        for rec in self:
            rec.is_gre = self.env.user.has_group('visa_process.group_service_request_employee')
    
    @api.depends("from_date", "to_date")
    def _compute_days(self):
        for record in self:
            if record.from_date and record.to_date:
                if record.to_date < record.from_date:
                    raise ValidationError("To Date cannot be before From Date.")
                delta = record.to_date - record.from_date
                record.number_of_days = delta.days + 1
            else:
                record.number_of_days = 0

    def action_submit(self):
        for record in self:
            record.state = 'submit'

    def action_pm_submit(self):
        for record in self:
            record.state = 'submitted_to_gre'

    def action_done(self):
        for record in self:
            if not record.ref_no_snapshot:
                raise ValidationError('Please update Reference Number')
            record.state = 'done'

    def action_pm_reject(self):
        for record in self:
            record.state = 'reject'


                