# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
import re
import logging

_logger = logging.getLogger(__name__)

class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'

    service_request = fields.Selection(
        selection_add=[
            ('probation_request', 'Extend Probation')
        ],
        string="Service Requests",
        store=True,
        copy=False,
        ondelete={'probation_request': 'cascade'}

    )

    # New field to display calculated probation end date
    calculated_probation_end_date = fields.Date(
        string="Probation End Date",
        compute='_compute_probation_end_date',
        store=True,
    )
    extended_employment_duration = fields.Selection([('3','3 Months'),('6','6 Months'),('9','9 Months'),('12','12 Months'),
        ('15','15 Months'),('18','18 Months'),('21','21 Months'),('24','24 Months')],string="Duration of Employment *",tracking=True)
    extended_probation_term = fields.Char(string="Probation Term",tracking=True)
    upload_probation_doc = fields.Binary(string="Probation Period Letter")
    probation_doc_ref = fields.Char(string="Ref No")
    upload_probation_doc_file_name = fields.Char(string="Probation Period Letter")
    upload_qiwa_modified_doc = fields.Binary(string="Qiwa Modified Document")
    qiwa_modified_doc_ref = fields.Char(string="Ref No")
    upload_qiwa_modified_doc_file_name = fields.Char(string="Qiwa Modified Document")
    upload_qiwa_acceptace_doc = fields.Binary(string="Qiwa Acceptance Document")
    qiwa_acceptance_doc_ref = fields.Char(string="Ref No")
    upload_qiwa_acceptace_doc_file_name = fields.Char(string="Qiwa Acceptance Document")
    upload_signed_doc = fields.Binary(string="Signed Letter from Employee")
    signed_doc_ref = fields.Char(string="Ref No")
    upload_signed_doc_file_name = fields.Char(string="Signed Letter from Employee")


    @api.depends('doj', 'probation_term')
    def _compute_probation_end_date(self):
        """
        Calculate probation end date based on DOJ and probation term
        """
        for record in self:
            record.calculated_probation_end_date = False
            
            if not record.doj or not record.probation_term:
                continue
                
            try:
                # Parse the probation term to get the duration
                term = record.probation_term.strip().lower()
                value = 0
                
                if 'day' in term:
                    # Extract number of days
                    numbers = re.findall(r'\d+', term)
                    if numbers:
                        value = int(numbers[0])
                    record.calculated_probation_end_date = record.doj + timedelta(days=value)
                    
                elif 'week' in term:
                    # Extract number of weeks
                    numbers = re.findall(r'\d+', term)
                    if numbers:
                        value = int(numbers[0])
                    record.calculated_probation_end_date = record.doj + timedelta(weeks=value)
                    
                elif 'month' in term:
                    # Extract number of months
                    numbers = re.findall(r'\d+', term)
                    if numbers:
                        value = int(numbers[0])
                    record.calculated_probation_end_date = record.doj + relativedelta(months=value)
                    
                else:
                    # Try to parse as direct number (assume days)
                    try:
                        value = int(term)
                        record.calculated_probation_end_date = record.doj + timedelta(days=value)
                    except ValueError:
                        # If it's not a number, try to extract any number from the string
                        numbers = re.findall(r'\d+', term)
                        if numbers:
                            value = int(numbers[0])
                            record.calculated_probation_end_date = record.doj + timedelta(days=value)
                            
            except Exception as e:
                # Log the error but don't break the computation
                _logger.warning(f"Error calculating probation end date for record {record.id}: {str(e)}")
                record.calculated_probation_end_date = False

    @api.onchange('employee_id')
    def _onchange_employee_probation_info(self):
        """
        Update probation information when employee is changed
        """
        if self.employee_id:
            # Update DOJ and probation term from employee
            if self.employee_id.doj:
                self.doj = self.employee_id.doj
            if self.employee_id.probation_term:
                self.probation_term = self.employee_id.probation_term

    def action_view_probation_info(self):
        """
        Action to view probation information in a popup
        """
        self.ensure_one()
        
        if not self.employee_id:
            raise UserError(_("Please select an employee first."))
            
        if not self.doj or not self.probation_term:
            raise UserError(_("Please ensure both Date of Joining and Probation Term are filled."))
            
        return {
            'name': _('Probation Information'),
            'type': 'ir.actions.act_window',
            'res_model': 'service.enquiry',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_doj': self.doj,
                'default_probation_term': self.probation_term,
                'default_calculated_probation_end_date': self.calculated_probation_end_date,
            }
        }

    def get_probation_status(self):
        """
        Get probation status for the employee
        Returns: 'active', 'expired', 'upcoming', or 'no_probation'
        """
        self.ensure_one()
        
        if not self.calculated_probation_end_date:
            return 'no_probation'
            
        today = fields.Date.today()
        
        if self.calculated_probation_end_date < today:
            return 'expired'
        elif self.calculated_probation_end_date == today:
            return 'expires_today'
        elif self.calculated_probation_end_date <= today + timedelta(days=15):
            return 'upcoming'
        else:
            return 'active'

    def get_days_remaining(self):
        """
        Get days remaining in probation period
        Returns: Number of days remaining (negative if expired)
        """
        self.ensure_one()
        
        if not self.calculated_probation_end_date:
            return 0
            
        today = fields.Date.today()
        delta = self.calculated_probation_end_date - today
        return delta.days
    def open_assign_employee_wizard(self):
        """Inherit open_assign_employee_wizard to add validation for visa cancellation"""
        for record in self:
            if record.service_request == 'probation_request':
                # Validate required fields for visa cancellation
                if not record.extended_employment_duration:
                    raise ValidationError(_("Please select Employment Duration"))
                if not record.extended_probation_term:
                    raise ValidationError(_("Please provide the probation term"))
        # Call the parent method
        return super(ServiceEnquiry, self).open_assign_employee_wizard()

    def action_doc_uploaded_probation(self):
        for record in self:
            if record.service_request == 'probation_request':
                if record.upload_qiwa_modified_doc and not record.qiwa_modified_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Doc")
                if record.upload_probation_doc and not record.probation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Probation Doc")
                record.state = 'submit_to_pm'  
                record.dynamic_action_status = "Document uploaded by first government Employee, review by PM is pending"
                record.action_user_id= record.approver_id.user_id.id
                record.write({'processed_date': fields.Datetime.now()})
    def _calculate_new_probation_end_date(self, record):
        """
        Calculate new probation end date based on extended probation term
        """
        if not record.doj or not record.extended_probation_term:
            return False
            
        try:
            # Parse the extended probation term to get the duration
            term = record.extended_probation_term.strip().lower()
            value = 0
            
            if 'day' in term:
                # Extract number of days
                numbers = re.findall(r'\d+', term)
                if numbers:
                    value = int(numbers[0])
                return record.doj + timedelta(days=value)
                
            elif 'week' in term:
                # Extract number of weeks
                numbers = re.findall(r'\d+', term)
                if numbers:
                    value = int(numbers[0])
                return record.doj + timedelta(weeks=value)
                
            elif 'month' in term:
                # Extract number of months
                numbers = re.findall(r'\d+', term)
                if numbers:
                    value = int(numbers[0])
                return record.doj + relativedelta(months=value)
                
            else:
                # Try to parse as direct number (assume days)
                try:
                    value = int(term)
                    return record.doj + timedelta(days=value)
                except ValueError:
                    # If it's not a number, try to extract any number from the string
                    numbers = re.findall(r'\d+', term)
                    if numbers:
                        value = int(numbers[0])
                        return record.doj + timedelta(days=value)
                        
        except Exception as e:
            return False
            
        return False

    def action_process_complete_probation(self):
        for record in self:
            if record.service_request == 'probation_request':
                if record.upload_qiwa_acceptace_doc and not record.qiwa_acceptance_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Qiwa Doc")
                if record.upload_signed_doc and not record.signed_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Signed Doc")
                
                # Validate required fields for probation extension
                if not record.extended_employment_duration:
                    raise ValidationError(_("Please set the Extended Employment Duration before completing the process."))
                if not record.extended_probation_term:
                    raise ValidationError(_("Please set the Extended Probation Term before completing the process."))
                
                # Update employee's employment_duration and probation_term
                if record.employee_id and (record.extended_employment_duration or record.extended_probation_term):
                    employee_update_vals = {}
                    
                    # Update employment_duration if extended_employment_duration is set
                    if record.extended_employment_duration:
                        employee_update_vals['employment_duration'] = record.extended_employment_duration
                    
                    # Update probation_term if extended_probation_term is set
                    if record.extended_probation_term:
                        employee_update_vals['probation_term'] = record.extended_probation_term
                        
                        # Calculate and update probation_end_date based on new probation term
                        new_probation_end_date = self._calculate_new_probation_end_date(record)
                        if new_probation_end_date:
                            employee_update_vals['probation_end_date'] = new_probation_end_date
                    
                    # Apply the updates to the employee
                    if employee_update_vals:
                        try:
                            record.employee_id.sudo().write(employee_update_vals)
                            
                            # Post a message to the service enquiry record
                            update_message = _("Employee probation details updated:")
                            if record.extended_employment_duration:
                                update_message += f" Employment Duration: {record.extended_employment_duration} months"
                            if record.extended_probation_term:
                                update_message += f", Probation Term: {record.extended_probation_term}"
                            if 'probation_end_date' in employee_update_vals:
                                update_message += f", New End Date: {employee_update_vals['probation_end_date']}"
                            record.message_post(body=update_message)
                            
                        except Exception as e:
                            raise ValidationError(f"Failed to update employee probation details: {str(e)}")
                
                record.state = 'done'  
                record.dynamic_action_status = "Process Completed"
                record.action_user_id= False
                record.write({'processed_date': fields.Datetime.now()})