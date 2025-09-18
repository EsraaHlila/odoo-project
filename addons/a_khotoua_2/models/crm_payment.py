from odoo import models, fields

class CrmPayment(models.Model):
    _name = 'crm.payment'
    _description = 'CRM Payment'

    name = fields.Char(required=True)
    subscription_id = fields.Many2one('crm.subscription', string="Subscription")
    amount = fields.Float()
    payment_date = fields.Date()
