# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceRequestTreasury(models.Model):
    _inherit = 'service.request.treasury'

    def action_submit_to_treasury_visa_cancellation(self):
        """Submit visa cancellation request to treasury"""
        for record in self:
            if record.service_request_id.service_request == 'visa_cancellation':
                record.state = 'submitted'
                record.service_request_id.state = 'submitted_to_treasury'
                record.service_request_id.dynamic_action_status = f'Submitted to the Treasury Department. Document upload confirmation is pending.'
                record.service_request_id.write({'processed_date': fields.Datetime.now()})

    def action_upload_confirmation(self):
        super(ServiceRequestTreasury, self).action_upload_confirmation()
        """Upload confirmation for visa cancellation treasury request"""
        for record in self:
            if record.service_request_id.service_request == 'visa_cancellation':
                if record.confirmation_doc and not record.confirmation_doc_ref:
                    raise ValidationError("Kindly Update Reference Number for Confirmation Document")
                if not record.issue_date:
                    raise ValidationError("Kindly update issue date before upload confirmation")
                # Update the service enquiry with confirmation document
                record.service_request_id.write({'upload_payment_doc': record.confirmation_doc})
                record.service_request_id.write({'payment_doc_ref':record.confirmation_doc_ref})
                record.state = 'done'
                record.service_request_id.state = 'done'
                record.service_request_id.dynamic_action_status = "Process completed"
                record.service_request_id.action_user_id=False
                record.service_request_id.write({'processed_date': fields.Datetime.now()})
