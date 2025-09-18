from odoo import models, fields

class Enterprise(models.Model):
    _name = 'enterprise.manager'
    _description = 'Enterprise'

    name = fields.Char(string='Enterprise Name', required=True)
    enterprise_type = fields.Selection([
        ('private', 'Private'),
        ('public', 'Public'),
        ('ngo', 'NGO'),
    ], string='Type')
    registration_number = fields.Char(string='Registration Number')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    website = fields.Char(string='Website')
