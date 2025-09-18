from odoo import models, fields

class CRMSubscription(models.Model):
    _name = 'crm.subscription'
    _description = 'User Subscriptions'

    user_id = fields.Many2one('crm.user', string="User")
    plan_name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ])
