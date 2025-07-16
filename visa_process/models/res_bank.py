# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil import relativedelta as rdelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    employee_id = fields.Many2one('hr.employee',string="Account Holder",ondelete='cascade',index=True)
    partner_id = fields.Many2one('res.partner', 'Account Holder', ondelete='cascade', index=True, domain=['|', ('is_company', '=', True), ('parent_id', '=', False)], required=False)


    @api.model
    def create(self, vals):
        print("------tets")
        if vals.get('employee_id') and not vals.get('partner_id'):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            print("-------empl vals",employee)
            
            # Check if partner already exists (optional)
            partner = employee.address_home_id
            if not partner:
                partner_vals = {
                    'name': employee.name,
                    'company_id': employee.company_id.id,
                    'type': 'private',
                    'custom_employee_type': employee.custom_employee_type,
                    'email': employee.work_email,
                    'phone': employee.work_phone or employee.mobile_phone,
                    'street': employee.address_id.street if employee.address_id else '',
                    'city': employee.address_id.city if employee.address_id else '',
                    'state_id': employee.address_id.state_id.id if employee.address_id else False,
                    'country_id': employee.address_id.country_id.id if employee.address_id else False,
                }
                partner = self.env['res.partner'].create(partner_vals)
                print("----------partnerrrrrr",partner)

                # Optionally link back to employee
                employee.address_home_id = partner.id

            vals['partner_id'] = partner.id

        return super().create(vals)