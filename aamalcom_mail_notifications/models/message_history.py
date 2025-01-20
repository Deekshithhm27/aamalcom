from odoo import models, fields, api, _


class MessageHistory(models.Model):
    _name = 'message.history'
    _description = 'Message History'

    service_enquiry_id = fields.Many2one('service.enquiry', string="Service Enquiry")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    sender = fields.Many2one('res.users', string="Sender")
    message = fields.Text(string="Message")