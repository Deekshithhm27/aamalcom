from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError
from datetime import date
from odoo.tools import date_utils


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # -------------------------------------------------------------------------
    # Extra workflow states
    # -------------------------------------------------------------------------
    state = fields.Selection(selection_add=[
        ('hr_specialist', 'Review'),
        ('hr_manager', 'HR Manager Review'),
        ('gm_approve', 'GM Approval'),
    ], ondelete={
        'hr_specialist': 'cascade',
        'hr_manager': 'cascade',
        'gm_approve': 'cascade'
    })

    # -------------------------------------------------------------------------
    # Extra Fields
    # -------------------------------------------------------------------------
    leave_type_name = fields.Char(
        string='Leave Type Name',
        compute='_compute_leave_type_name',
        store=True
    )
    replacement_id = fields.Many2one('hr.employee', string='Replacement Employee',domain="[('custom_employee_type','=','internal')]")
    is_saudi = fields.Boolean(string='Is Saudi', compute='_compute_is_saudi')
    exit_reentry = fields.Boolean(string='Exit Reentry')
    service_request_id = fields.Many2one('service.enquiry',string='ERE Source',domain="[('service_request', '=', 'exit_reentry_issuance'),('employee_id','=',employee_id)]")
    is_ticket = fields.Boolean(string='Is Ticket Available?')
    ticket_doc = fields.Binary(string='Ticket')
    ere_dates = fields.Char(string='ERE Dates')
    hajj_permission = fields.Binary(string='Hajj Permission')
    invitation = fields.Binary(string='Marriage Invitation')
    birth_certificate = fields.Binary(string='Birth Certificate')
    death_certificate = fields.Binary(string='Death Certificate')
    relationship = fields.Char(string='Relationship (for Bereavement)')
    emergency_reason = fields.Text(string='Emergency Reason')
    emergency_documents = fields.Binary(string='Emergency Documents')
    refuse_reason = fields.Text(string='Refuse Reason')

    passport_front = fields.Binary(string="Passport Front")
    passport_back = fields.Binary(string="Passport Back")

    document_note = fields.Text(
        string="Supporting Documents Note",
        help="Mention details about supporting documents (attach files in chatter)."
    )

    @api.onchange('holiday_status_id')
    def _onchange_leave_type_set_document_note(self):
        """ Auto update note based on leave type """
        if not self.holiday_status_id:
            return

        leave_type_name = self.holiday_status_id.name or ''
        notes_map = {
            'Annual Vacation': "Please mention passport details in notes and attach in chatter.",
            'Sick Leave': "Please mention sick leave report in notes and attach in chatter.",
            'Hajj Vacation': "Please mention Hajj permission in notes and attach in chatter.",
            'Marriage Leave': "Please mention invitation details in notes and attach in chatter.",
            'Maternity Leave': "Please mention birth certificate in notes and attach in chatter.",
            'Paternity Leave': "Please mention birth certificate in notes and attach in chatter.",
            'Bereavement Leave': "Please mention death certificate & relationship in notes and attach in chatter.",
            'Emergency Vacation': "Please provide emergency reason and attach documents in chatter.",
        }

        self.document_note = notes_map.get(leave_type_name, "")

    # -------------------------------------------------------------------------
    # Computes
    # -------------------------------------------------------------------------
    @api.depends('holiday_status_id')
    def _compute_leave_type_name(self):
        for leave in self:
            leave.leave_type_name = leave.holiday_status_id.name or ''

    @api.depends('employee_id')
    def _compute_is_saudi(self):
        for leave in self:
            leave.is_saudi = (leave.employee_id.country_id.code == 'SA')

    @api.depends('holiday_status_id')
    def _compute_state(self):
        for leave in self:
            leave.state = 'confirm' if leave.validation_type != 'no_validation' else 'draft'



    # -------------------------------------------------------------------------
    # Workflow overrides
    # -------------------------------------------------------------------------
    def action_approve(self):
        """ Employee submits → goes to HR Specialist first. """
        res = super(HrLeave, self).action_approve()
        for leave in self:
            if leave.leave_type_name == 'Work Remotely':
                leave.state = 'hr_specialist'
        return res


    def action_validate(self):
        """ Final GM approval triggers standard validation. """
        return super(HrLeave, self).action_validate()

    # -------------------------------------------------------------------------
    # New workflow actions
    # -------------------------------------------------------------------------
    def action_hr_specialist_approve(self):
        # if not self.env.user.has_group('visa_process.group_service_request_employee'):
        #     raise ValidationError(_('Only HR Specialist can approve this step.'))
        self.state = 'gm_approve'
        return True

    # def action_hr_manager_approve(self):
    #     if not self.env.user.has_group('visa_process.group_service_request_hr_manager'):
    #         raise ValidationError(_('Only HR Manager can approve this step.'))
    #     self.state = 'gm_approve'
    #     return True

    def action_gm_forward(self):
        if not self.env.user.has_group('visa_process.group_service_request_general_manager'):
            raise ValidationError(_('Only General Manager can approve this step.'))
        self.state = 'validate1'
        return True

    # -------------------------------------------------------------------------
    # Custom Validations
    # -------------------------------------------------------------------------
    @api.constrains('date_from', 'date_to', 'number_of_days', 'holiday_status_id', 'employee_id')
    def _check_custom_validations(self):
        for leave in self:
            leave_type_name = leave.holiday_status_id.name
            today = fields.Date.today()

            if not leave.date_from or not leave.date_to:
                continue

            delta = leave.date_from.date() - today

            # Fixed days check
            fixed_days = leave.holiday_status_id.fixed_days
            if fixed_days and leave.number_of_days != fixed_days:
                raise ValidationError(
                    _('Leave type %s requires exactly %s days.') % (leave_type_name, fixed_days)
                )

            # Balance check (skip for unpaid)
            if not leave.holiday_status_id.unpaid:
                allocation = self.env['hr.leave.allocation'].search([
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', leave.holiday_status_id.id),
                    ('state', '=', 'validate')
                ])
                remaining = sum(allocation.mapped('number_of_days')) - sum(
                    self.env['hr.leave'].search([
                        ('employee_id', '=', leave.employee_id.id),
                        ('holiday_status_id', '=', leave.holiday_status_id.id),
                        ('state', '=', 'validate')
                    ]).mapped('number_of_days'))
                if leave.number_of_days > remaining:
                    raise ValidationError(
                        _('Cannot request more than remaining balance: %s days') % remaining
                    )

            # Department overlap (Annual, Sick)
            if leave_type_name in ['Annual Vacation', 'Sick Leave']:
                overlapping = self.search([
                    ('id', '!=', leave.id),
                    ('employee_id.department_id', '=', leave.employee_id.department_id.id),
                    ('state', 'in', ('validate', 'gm_approve')),
                    ('date_from', '<=', leave.date_to),
                    ('date_to', '>=', leave.date_from),
                ])
                print("------over lapping",overlapping)
                if overlapping:
                    raise ValidationError(
                        _('No two employees from the same department can be on leave together.')
                    )

            # Annual Vacation rules
            if leave_type_name == 'Annual Vacation':
                notice_days = 14 if leave.is_saudi else (60 if leave.exit_reentry and leave.is_ticket else 14)
                if delta.days < notice_days:
                    raise ValidationError(
                        _('Must submit %s days in advance for Annual Vacation.') % notice_days
                    )
                # if not (leave.passport_front and leave.passport_back):
                #     raise ValidationError(_('Passport copies (front and back) required.'))

            # # Sick Leave
            # elif leave_type_name == 'Sick Leave':
            #     if not leave.sick_leave_report:
            #         raise ValidationError(_('Sick leave report required.'))

            # Work Remotely
            elif leave_type_name == 'Work Remotely':
                quarter_start, quarter_end = date_utils.get_quarter(leave.date_from.date())
                previous = self.search_count([
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', leave.holiday_status_id.id),
                    ('state', '=', 'validate'),
                    ('date_from', '>=', quarter_start),
                    ('date_from', '<=', quarter_end),
                ])
                if previous >= 1:
                    raise ValidationError(_('Only one remote work leave per quarter allowed.'))

            # Hajj Vacation
            elif leave_type_name == 'Hajj Vacation':
                if leave.employee_id.religion != 'muslim':
                    raise ValidationError(_('Hajj Vacation is only for Muslim employees.'))
                contract = leave.employee_id.contract_id.filtered(lambda c: c.state == 'open')
                print('-------contract',contract)
                if contract and (today - contract.date_start).days < 730:
                    raise ValidationError(_('Must have 2 years of contract duration for Hajj Vacation.'))
                # if not leave.hajj_permission:
                #     raise ValidationError(_('Hajj permission document required.'))

            # Marriage
            elif leave_type_name == 'Marriage Leave':
                if not leave.invitation:
                    raise ValidationError(_('Marriage invitation required.'))

            # Maternity & Paternity
            elif leave_type_name in ['Maternity Leave', 'Paternity Leave']:
                if not leave.birth_certificate:
                    raise ValidationError(_('Birth certificate required.'))

            # Bereavement
            elif leave_type_name == 'Bereavement Leave':
                if not (leave.death_certificate and leave.relationship):
                    raise ValidationError(_('Death certificate and relationship required.'))

            # Emergency
            elif leave_type_name == 'Emergency Vacation':
                if not (leave.emergency_reason and leave.emergency_documents):
                    raise ValidationError(_('Emergency reason and documents required.'))

    # def action_approve(self):
    #     """
    #     Manager approval:
    #      - For validation_type == 'both' we want a two-step approval.
    #        Instead of moving directly to validate1, manager approval sends it to HR Specialist
    #        (custom state 'hr_specialist'), and we record first_approver_id.
    #      - For other types, behave as standard (i.e., call action_validate()).
    #     """
    #     if any(holiday.state != 'confirm' for holiday in self):
    #         raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

    #     current_employee = self.env.user.employee_id

    #     # Manager approves: if two-step validation required, send to HR Specialist (custom)
    #     both = self.filtered(lambda hol: hol.validation_type == 'both')
    #     if both:
    #         # record manager as first approver and set to hr_specialist
    #         both.write({'state': 'hr_specialist', 'first_approver_id': current_employee.id})

    #         # notify employee(s)
    #         for holiday in both.filtered(lambda holiday: holiday.employee_id.user_id):
    #             try:
    #                 user_tz = timezone(holiday.tz)
    #                 utc_tz = pytz.utc.localize(holiday.date_from).astimezone(user_tz)
    #                 holiday.message_post(
    #                     body=_(
    #                         'Your %(leave_type)s planned on %(date)s has been accepted by Manager and is sent to HR Specialist for review.',
    #                         leave_type=holiday.holiday_status_id.display_name,
    #                         date=utc_tz.replace(tzinfo=None)
    #                     ),
    #                     partner_ids=holiday.employee_id.user_id.partner_id.ids)
    #             except Exception:
    #                 # fallback simpler message if tz conversion fails
    #                 holiday.message_post(body=_('Your %s has been accepted by Manager and sent to HR Specialist for review.') % holiday.holiday_status_id.display_name)

    #     # For requests that don't require two-step validation, validate immediately
    #     others = self.filtered(lambda hol: hol.validation_type != 'both')
    #     if others:
    #         others.action_validate()

    #     if not self.env.context.get('leave_fast_create'):
    #         # update activities for those still in pipeline
    #         self.activity_update()
    #     return True

    # ------------------------------
    # HR Specialist approves -> forward to HR Manager (validate1)
    # ------------------------------
    # def action_hr_specialist_approve(self):
    #     """
    #     Called by HR Specialist (group: HR Specialist or HR Officer).
    #     Moves state from 'hr_specialist' -> 'validate1' (HR manager step).
    #     """
    #     # permission check: adjust group xml_ids as per your env
    #     if not (self.env.user.has_group('visa_process.group_service_request_employee') or self.env.user.has_group('visa_process.group_service_request_hr_manager')):
    #         raise UserError(_('Only HR Specialist or HR Manager can perform this action.'))

    #     current_employee = self.env.user.employee_id
    #     # Only allow on items in hr_specialist state
    #     to_forward = self.filtered(lambda hol: hol.state == 'hr_specialist')
    #     if not to_forward:
    #         raise UserError(_('No leave requests are waiting for HR Specialist approval.'))

    #     # set to validate1 and set first_approver if not set
    #     to_forward.write({'state': 'validate1', 'first_approver_id': current_employee.id})
    #     # notify employee(s)
    #     for holiday in to_forward.filtered(lambda holiday: holiday.employee_id.user_id):
    #         holiday.message_post(body=_('Your %(leave_type)s has been reviewed by HR Specialist and forwarded to HR Manager for approval.', leave_type=holiday.holiday_status_id.display_name))
    #     # schedule activity for HR Manager
    #     if to_forward:
    #         try:
    #             hr_mgr_group = self.env.ref('visa_process.group_service_request_hr_manager', raise_if_not_found=False)
    #             if hr_mgr_group and hr_mgr_group.users:
    #                 for u in hr_mgr_group.users[:1]:
    #                     to_forward.activity_schedule('mail.mail_activity_data_todo', summary=_('Approve Time Off Request'), note=_('Please approve the time off request.'), user_id=u.id)
    #         except Exception:
    #             pass
    #     return True

    # ------------------------------
    # action_validate (final validation) — allow being called from gm_approve
    # ------------------------------
    # def action_validate(self):
    #     """
    #     Final validation — allow validation when state is 'confirm', 'validate1' or 'gm_approve'.
    #     Otherwise keep original safety checks.
    #     """
    #     current_employee = self.env.user.employee_id

    #     # Reject if public holiday conflict
    #     leaves = self._get_leaves_on_public_holiday()
    #     if leaves:
    #         raise ValidationError(_('The following employees are not supposed to work during that period:\n %s') % ','.join(leaves.mapped('employee_id.name')))

    #     # allow if state in confirm/validate1/gm_approve or validation_type == 'no_validation'
    #     invalid = any(holiday.state not in ['confirm', 'validate1', 'gm_approve'] and holiday.validation_type != 'no_validation' for holiday in self)
    #     if invalid:
    #         raise UserError(_('Time off request must be confirmed in order to approve it.'))

    #     # keep the rest of the original implementation (split/overlap handling)
    #     # copy the original action_validate implementation here (or call super where appropriate)
    #     # For simplicity and safety call super() when our state checks are satisfied:
    #     return super(HrLeave, self).action_validate()

    
    # ------------------------------
    # _check_approval_update
    # ------------------------------
    # def _check_approval_update(self, state):
    #     """ Check if target state is achievable — extended to handle HR Specialist and GM roles. """
    #     if self.env.is_superuser():
    #         return

    #     current_employee = self.env.user.employee_id
    #     is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
    #     is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

    #     # custom groups
    #     is_ops_manager = self.env.user.has_group('visa_process.group_service_request_manager')
    #     is_hr_specialist = self.env.user.has_group('visa_process.group_service_request_employee')  # your HR Specialist group
    #     is_hr_manager = self.env.user.has_group('visa_process.group_service_request_hr_manager')
    #     is_gm = self.env.user.has_group('visa_process.group_service_request_general_manager')

    #     for holiday in self:
    #         val_type = holiday.validation_type

    #         # allow superuser, hr manager, gm
    #         if is_gm:
    #             continue

    #         if not is_manager and state != 'confirm':
    #             if state == 'draft':
    #                 if holiday.state == 'refuse':
    #                     raise UserError(_('Only a Time Off Manager can reset a refused leave.'))
    #                 if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
    #                     raise UserError(_('Only a Time Off Manager can reset a started leave.'))
    #                 if holiday.employee_id != current_employee:
    #                     raise UserError(_('Only a Time Off Manager can reset other people leaves.'))
    #             else:
    #                 if val_type == 'no_validation' and current_employee == holiday.employee_id:
    #                     continue
    #                 holiday.check_access_rule('write')

    #                 # Prevent approving own request
    #                 if holiday.employee_id == current_employee:
    #                     raise UserError(_('Only a Time Off Manager can approve/refuse its own requests.'))

    #                 # Custom checks: allow HR Specialist to move hr_specialist -> validate1
    #                 if state == 'validate1' and val_type == 'both' and holiday.state == 'hr_specialist':
    #                     if not (is_hr_specialist or is_hr_manager):
    #                         raise UserError(_('Only HR Specialist or HR Manager can move from HR Specialist review to HR Manager approval.'))

    #                 # HR Manager -> GM forwarding
    #                 if state == 'gm_approve' and holiday.state in ['validate1', 'hr_specialist']:
    #                     if not is_hr_manager:
    #                         raise UserError(_('Only HR Manager can forward the request to GM.'))

    #                 # GM final validation will be handled by action_validate with group check
    #                 # Manager permission: if state is validate and val_type == 'manager', ensure manager is the approver
    #                 if (state == 'validate' and val_type == 'manager') and self.env.user != (holiday.employee_id | holiday.sudo().employee_ids).leave_manager_id:
    #                     raise UserError(_('You must be %s\'s Manager to approve this leave') % (holiday.employee_id.name,))

    #     return