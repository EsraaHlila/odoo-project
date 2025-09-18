from odoo import models, fields

class CRMUser(models.Model):
    _name = 'crm.user'
    _description = 'App Users'

    name = fields.Char(required=True)
    email = fields.Char()
    role = fields.Char()
    created_at = fields.Datetime()
