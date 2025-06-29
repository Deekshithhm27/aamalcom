# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError,UserError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ServiceEnquiry(models.Model):
    _inherit = 'service.enquiry'
    
    def action_process_complete(self):
        for record in self:
            if record.service_request == 'hr_card':
                swapping_id = self.env['swapping.border.to.iqama'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id':record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id':record.employee_id.id,
                    'swapping_type':'employee',
                    'project_manager_id':record.client_id.company_spoc_id.id,
                    'residance_doc':record.residance_doc,
                    'muqeem_print_doc'record.muqeem_print_doc
                })
            if record.service_request == 'final_exit_issuance':
                medical_insurance_deletion = self.env['medical.insurance.deletion'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id':record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id':record.employee_id.id,
                    'deletion_type':'final_exit',
                })
                life_insurance_deletion = self.env['life.insurance.deletion'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id':record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id':record.employee_id.id,
                    'deletion_type':'final_exit',
                })
            if record.service_request == 'transfer_req' and record.transfer_type == 'to_another_establishment':
            	life_insurance_deletion = self.env['life.insurance.deletion'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id':record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id':record.employee_id.id,
                    'deletion_type':'iqama_transfer',
                })
                medical_insurance_deletion = self.env['medical.insurance.deletion'].create({
                    'client_id': record.client_id.id,
                    'client_parent_id':record.client_id.parent_id.id,
                    'service_enquiry_id': record.id,
                    'employee_id':record.employee_id.id,
                    'deletion_type':'iqama_transfer',
                })
        return super(ServiceEnquiry, self).action_process_complete()


        