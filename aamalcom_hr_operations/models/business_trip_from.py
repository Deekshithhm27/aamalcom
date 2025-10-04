from odoo import models, fields, api
from odoo.exceptions import UserError

class BusinessTripForm(models.Model):
	_name = 'business.trip.form'

	name = fields.Char(string="Name")
	business_trip_form = fields.Binary(string="Business Trip Form")