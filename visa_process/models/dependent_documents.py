# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class DependentDocuments(models.Model):
    _name = "dependent.documents"
    _description = "Documents Line"

    ev_dependent_document_id = fields.Many2one('employment.visa',string="Employment Visa Id")
    lt_dependent_document_id = fields.Many2one('local.transfer',string="Local Transfer Id")

    ev_enq_dependent_document_id = fields.Many2one('service.enquiry',string="EV Enq Id")

    person_name = fields.Char(string="Document Belongs to ?",required=True)
    
    dependent_passport_id = fields.Binary(string="Dependent Passport")
    dependent_iqama_id = fields.Binary(string="Dependent Iqama")
    dependent_border_id = fields.Binary(string="Dependent Border Id")
    visa_page = fields.Binary(string="Visa Page")
