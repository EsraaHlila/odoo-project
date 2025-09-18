from odoo import models, fields

class CrmUser(models.Model):
    _name = 'crm.user'
    _description = 'CRM User'

    name = fields.Char(required=True)
    email = fields.Char()
    role = fields.Selection([
        ('sales', 'Sales'),
        ('support', 'Support'),
        ('admin', 'Admin'),
    ], string='Role')
