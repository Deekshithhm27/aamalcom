# File: my_training_module/models/training_course.py

from odoo import models, fields, api

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Training Details'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Training Title', required=True, tracking=True)
    description = fields.Html(string='Description', tracking=True)
    purpose = fields.Html(string='Purpose of Training', tracking=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    timings = fields.Char(string='Timings', tracking=True, help="e.g., 9:00 AM - 5:00 PM")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], string='Status', default='draft', required=True, tracking=True)
    accepted_by_user_ids = fields.Many2many('res.users', string='Accepted By', readonly=True)

    def action_submit(self):
        self.ensure_one()
        self.state = 'submitted'


    def action_accept(self):
        self.ensure_one()
        # Add the current user to the accepted_by_user_ids list
        self.accepted_by_user_ids = [(4, self.env.user.id)]

    def action_later_review(self):
        self.ensure_one()
        # The user's action is recorded in the chatter but no list is updated
        self.message_post(body="The training has been marked for later review.")

