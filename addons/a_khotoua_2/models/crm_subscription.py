from odoo import models, fields

class CrmSubscription(models.Model):
    _name = 'crm.subscription'
    _description = 'CRM Subscription'

    name = fields.Char(required=True)
    user_id = fields.Many2one('crm.user', string="CRM User")
    start_date = fields.Date()
    end_date = fields.Date()
    active = fields.Boolean(default=True)
