# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    days_remaining = fields.Integer(
        string="Days Remaining",
        compute='_compute_days_remaining',
        store=False,
        help="Days remaining until probation ends"
    )

    @api.depends('probation_end_date')
    def _compute_days_remaining(self):
        """Compute days remaining until probation ends"""
        today = fields.Date.context_today(self)
        for employee in self:
            if employee.probation_end_date:
                try:
                    probation_end_date = fields.Date.from_string(employee.probation_end_date)
                    if probation_end_date:
                        employee.days_remaining = (probation_end_date - today).days
                    else:
                        employee.days_remaining = 0
                except (ValueError, TypeError):
                    employee.days_remaining = 0
            else:
                employee.days_remaining = 0

    @api.model
    def cron_check_probation_ending_sr(self):
        """
        Cron job to check for employees whose probation is ending soon
        and send notifications to client SPOC and project managers
        """
        today = fields.Date.context_today(self)
        # Check for employees whose probation ends within 15 days
        limit_date = fields.Date.to_string(fields.Date.from_string(today) + timedelta(days=15))

        _logger.info(f"Checking for employees with probation ending between {today} and {limit_date}")

        # Find employees with probation ending soon
        employees = self.search([
            ('probation_end_date', '!=', False),
            ('probation_end_date', '!=', None),
            ('probation_end_date', '<=', limit_date),
            ('probation_end_date', '>=', today),
            ('custom_employee_type', '=', 'external'),  # Only external employees
            ('client_id', '!=', False),  # Must have a client SPOC
        ])

        _logger.info(f"Found {len(employees)} employees with probation ending soon")

        if not employees:
            _logger.info("No employees found with probation ending soon")
            return

        # Log employee details for debugging
        for emp in employees:
            _logger.info(f"Processing employee: {emp.name} (ID: {emp.id}), probation_end_date: {emp.probation_end_date}")

        # Get the email template
        mail_template = self.env.ref('sr_probation.email_template_probation_warning_sr', False)
        if not mail_template:
            _logger.error("Email template 'sr_probation.email_template_probation_warning_sr' not found")
            return

        # Get activity type for creating activities
        activity_type = self.env.ref('sr_probation.mail_activity_type_probation_notify_sr', False)
        if not activity_type:
            _logger.warning("Activity type 'sr_probation.mail_activity_type_probation_notify_sr' not found")

        for employee in employees:
            # Additional safety check for probation_end_date
            if not employee.probation_end_date:
                _logger.warning(f"Skipping employee {employee.name}: probation_end_date is None")
                continue
                
            # Check if there's already an open probation extension request
            has_open_request = self.env['hr.probation.extend.request'].search_count([
                ('employee_id', '=', employee.id),
                ('state', 'not in', ['done', 'cancelled']),
            ])

            if has_open_request:
                _logger.info(f"Skipping employee {employee.name}: already has an open probation extension request")
                continue  # Skip if there's already an open request

            # Get client SPOC and project manager
            client_spoc = employee.client_id
            project_manager = employee.company_spoc_id

            if not client_spoc or not project_manager:
                _logger.warning(f"Skipping employee {employee.name}: missing client_spoc or project_manager")
                continue  # Skip if missing required contacts

            # Remove old activities to avoid duplicates
            domain_activities = [
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', employee.id),
                ('activity_type_id', '=', activity_type.id if activity_type else False),
            ]
            self.env['mail.activity'].search(domain_activities).unlink()

            # Prepare email recipients
            email_recipients = []
            if client_spoc.partner_id.email:
                email_recipients.append(client_spoc.partner_id.email)
            if project_manager.work_email or project_manager.user_id.partner_id.email:
                pm_email = project_manager.work_email or project_manager.user_id.partner_id.email
                if pm_email and pm_email not in email_recipients:
                    email_recipients.append(pm_email)

            if not email_recipients:
                _logger.warning(f"Skipping employee {employee.name}: no valid email addresses found")
                continue  # Skip if no valid email addresses

            # Calculate days remaining with additional safety check
            try:
                probation_end_date = fields.Date.from_string(employee.probation_end_date)
                if not probation_end_date:
                    _logger.warning(f"Skipping employee {employee.name}: invalid probation_end_date format")
                    continue
                days_remaining = (probation_end_date - today).days
            except (ValueError, TypeError) as e:
                _logger.error(f"Error calculating days remaining for employee {employee.name}: {str(e)}")
                continue

            # Send email notification
            email_values = {
                'email_to': ','.join(email_recipients),
                'email_from': self.env.user.company_id.email or self.env.user.email,
                'auto_delete': True,
            }

            # Send email notification
            try:
                mail_template.send_mail(
                    employee.id, 
                    email_values=email_values, 
                    force_send=True
                )
                _logger.info(f"Probation notification email sent for employee {employee.name} to {email_recipients}")
            except Exception as e:
                _logger.error(f"Failed to send probation notification email for employee {employee.name}: {str(e)}")

            # Create activities for client SPOC and project manager
            if activity_type:
                # Activity for client SPOC
                if client_spoc.user_id:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'res_id': employee.id,
                        'user_id': client_spoc.user_id.id,
                        'activity_type_id': activity_type.id,
                        'summary': _('Probation ending soon for employee %s') % employee.name,
                        'note': _('Employee %s probation period ends on %s (%s days remaining). Please review and create extension request if needed.') % (
                            employee.name, employee.probation_end_date, days_remaining
                        ),
                        'date_deadline': fields.Date.today() + timedelta(days=7),
                    })

                # Activity for project manager
                if project_manager.user_id:
                    self.env['mail.activity'].create({
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'res_id': employee.id,
                        'user_id': project_manager.user_id.id,
                        'activity_type_id': activity_type.id,
                        'summary': _('Probation ending soon for employee %s') % employee.name,
                        'note': _('Employee %s probation period ends on %s (%s days remaining). Please review and create extension request if needed.') % (
                            employee.name, employee.probation_end_date, days_remaining
                        ),
                        'date_deadline': fields.Date.today() + timedelta(days=7),
                    })

        return True 