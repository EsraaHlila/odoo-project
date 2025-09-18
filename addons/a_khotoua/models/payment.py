from odoo import models, fields

class CRMPayment(models.Model):
    _name = 'crm.payment'
    _description = 'Payments'

    user_id = fields.Many2one('crm.user', string="User")
    subscription_id = fields.Many2one('crm.subscription', string="Subscription")
    amount = fields.Float()
    method = fields.Char()
    status = fields.Selection([
        ('success', 'Success'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ])
    payment_date = fields.Datetime()
