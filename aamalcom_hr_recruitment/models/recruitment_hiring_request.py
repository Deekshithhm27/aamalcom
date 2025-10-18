from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError

class HiringRequest(models.Model):
    _name = 'recruitment.hiring.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Hiring Request'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Request Reference', copy=False, readonly=True, default='New')
    active = fields.Boolean('Active', default=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    job_id = fields.Char('Job Position', required=True)  # User free text designation

    linked_hr_job_id = fields.Many2one('hr.job', string='Linked HR Job', readonly=True)

    department_id = fields.Many2one('hr.department', string='Department', store=True, readonly=True)
    number_of_positions = fields.Integer(string='Number of Positions', required=True)
    description = fields.Text(string='Description')
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, readonly=True)
    reject_reason = fields.Text('Rejection Reason', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('recruiter_approved', 'HR - Approved'),
        ('recruiter_rejected', 'HR - Rejected'),
        ('admin_approved', 'HR Manager - Approved'),
        ('admin_rejected', 'HR Manager - Rejected'),
        ('gm_approved', 'GM - Approved'),
        ('gm_rejected', 'GM - Rejected'),
        ('resumes_collecting', 'Resumes Collecting'),
        ('interviews', 'Interviews in Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    date_request = fields.Date(string='Request Date', default=fields.Date.context_today, readonly=True)

    resume_ids = fields.One2many('recruitment.hiring.request.resume', 'hiring_request_id', string="Resumes")

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'recruiter_rejected', 'admin_rejected', 'gm_rejected', 'cancel'):
                raise UserError(_("Cannot delete a request once it is approved or in progress."))
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.hiring.request') or 'New'
        return super().create(vals)

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only draft requests can be submitted."))
            rec.state = 'submitted'
            rec._notify_recruitment_officer_new_request()

    def action_officer_approve(self):
        """Recruitment Officer confirms request (submitted → recruiter_approved)"""
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_("Request must be in 'Submitted' state to confirm."))
            rec.state = 'recruiter_approved'
            rec.reject_reason = False
            rec._notify_recruitment_admin()

    def action_recruiter_reject(self):
        return self._open_reject_wizard('recruiter_rejected')

    def action_admin_approve(self):
        for rec in self:
            if rec.state != 'recruiter_approved':
                raise UserError(_("Request must be in recruiter approved state."))
            rec.state = 'admin_approved'
            rec.reject_reason = False
            rec._notify_general_manager()

    def action_admin_reject(self):
        return self._open_reject_wizard('admin_rejected')

    def action_gm_approve(self):
        for rec in self:
            if rec.state != 'admin_approved':
                raise UserError(_("Request must be in admin approved state."))

            rec.state = 'gm_approved'
            rec.reject_reason = False
            rec._notify_gm_approval()

    def action_gm_reject(self):
        return self._open_reject_wizard('gm_rejected')

    def action_start_resume_collection(self):
        HrJob = self.env['hr.job']
        """Called by HR Recruitment Officer after GM approval"""
        for rec in self:
            if rec.state != 'gm_approved':
                raise UserError(_("Request must be GM approved to start resume collection."))

            existing_job = HrJob.search([('name', '=', rec.job_id)], limit=1)
            if existing_job:
                rec.linked_hr_job_id = existing_job
                curr_state = existing_job.state if hasattr(existing_job, 'state') else False
                if curr_state == 'recruit':
                    existing_job.no_of_recruitment += rec.number_of_positions
                else:
                    existing_job.state = 'recruit'
                    existing_job.no_of_recruitment = rec.number_of_positions
            else:
                new_job = HrJob.create({
                    'name': rec.job_id,
                    'no_of_recruitment': rec.number_of_positions,
                    'company_id': rec.company_id.id,
                    'department_id': rec.department_id.id,
                    'user_id': self.env.user.id,
                    'state': 'recruit',
                })
                rec.linked_hr_job_id = new_job
            rec.state = 'resumes_collecting'
            rec._notify_recruiter_resume_collection()
    
    @api.onchange('linked_hr_job_id')
    def update_department_id(self):
        for line in self:
            if line.linked_hr_job_id.department_id and line.linked_hr_job_id:
                line.department_id = line.linked_hr_job_id.department_id
            if not line.linked_hr_job_id.department_id and line.department_id:
                line.linked_hr_job_id.department_id = line.department_id


    def action_initiate_interview_process(self):
        HrApplicant = self.env['hr.applicant']
        for rec in self:
            # if rec.state != 'resumes_collecting':
            #     raise UserError(_("You can initiate interview process only during resumes collecting stage."))

            shortlisted_resumes = rec.resume_ids.filtered(lambda r: r.state == 'shortlisted' and not r.application_ref)
            if not shortlisted_resumes:
                raise UserError(_("There are no shortlisted resumes to create applicants."))

            for resume in shortlisted_resumes:
                applicant = HrApplicant.create({
                    'name': resume.name,
                    'job_id': rec.linked_hr_job_id.id or False,
                    'email_from': resume.email or False,
                    'partner_name': resume.name,
                    'job_request_id':rec.id,
                    'stage_id': self.env['hr.recruitment.stage'].search([('sequence', '=', 1)], limit=1).id,
                })
                resume.application_ref = applicant.id

            rec.state = 'interviews'
            rec.message_post(body=_("Interview process started with %d shortlisted candidate(s)." % len(shortlisted_resumes)))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success 😊'),
                    'message': _('Job applications created from shortlisted resumes.'),
                    'type': 'success',
                    'sticky': False,  # If True, the notification stays until closed manually
                }
            }

    def action_complete(self):
        for rec in self:
            rec.linked_hr_job_id.state = 'open'
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def _open_reject_wizard(self, reject_state):
        return {
            'name': _('Provide Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'hiring.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_request_ids': self.ids, 'reject_state': reject_state},
        }

    def set_reject_reason(self, reason, reject_state):
        for rec in self:
            rec.reject_reason = reason
            rec.state = reject_state
            rec._notify_reject_communications(reject_state)

    # Add/adjust notify methods for new states accordingly:
    def _notify_recruitment_officer_new_request(self):
        group = self.env.ref('hr_recruitment.group_hr_recruitment_user', raise_if_not_found=False)
        if not group:
            return
        users = group.users.filtered(lambda u: u.email)
        emails = users.mapped('email')
        template = self.env.ref('aamalcom_hr_recruitment.email_template_new_hiring_request', False)
        for rec in self:
            if template and emails:
                template.email_to = ','.join(emails)
                template.send_mail(rec.id, force_send=True)

    def _notify_recruitment_admin(self):
        group = self.env.ref('hr_recruitment.group_hr_recruitment_manager', raise_if_not_found=False)
        if not group:
            return
        users = group.users.filtered(lambda u: u.email)
        emails = users.mapped('email')
        template = self.env.ref('aamalcom_hr_recruitment.email_template_recruiter_approval', False)
        for rec in self:
            if template and emails:
                template.email_to = ','.join(emails)
                template.send_mail(rec.id, force_send=True)

    def _notify_general_manager(self):
        group = self.env.ref('visa_process.group_service_request_general_manager', raise_if_not_found=False)
        if not group:
            return
        users = group.users.filtered(lambda u: u.email)
        emails = users.mapped('email')
        template = self.env.ref('aamalcom_hr_recruitment.email_template_admin_approval', False)
        for rec in self:
            if template and emails:
                template.email_to = ','.join(emails)
                template.send_mail(rec.id, force_send=True)

    def _notify_gm_approval(self):
        # Notify GM for approval
        self._notify_general_manager()

    def _notify_recruiter_resume_collection(self):
        group = self.env.ref('hr_recruitment.group_hr_recruitment_user', raise_if_not_found=False)
        if not group:
            return
        users = group.users.filtered(lambda u: u.email)
        emails = users.mapped('email')
        template = self.env.ref('aamalcom_hr_recruitment.email_template_gm_approval', False)
        for rec in self:
            if template and emails:
                template.email_to = ','.join(emails)
                template.send_mail(rec.id, force_send=True)

    def _notify_reject_communications(self, reject_state):
        template = self.env.ref('aamalcom_hr_recruitment.email_template_reject_notification', False)
        for rec in self:
            if template and rec.requested_by.partner_id.email:
                template.email_to = rec.requested_by.partner_id.email
                template.send_mail(rec.id, force_send=True)