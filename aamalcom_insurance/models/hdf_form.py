from odoo import models, fields, api
from odoo.exceptions import UserError

class HdfForm(models.Model):
	_name = 'hdf.form'

	name = fields.Char(string="Name")
	hdf_form = fields.Binary(string="HDF Form")