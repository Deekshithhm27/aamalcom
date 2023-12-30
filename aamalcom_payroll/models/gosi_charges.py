# -*- coding:utf-8 -*-

from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class GosiCharges(models.Model):
    _name = 'gosi.charges'
    _description = 'Gosi Charges'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Float(string="Gosi Percent")