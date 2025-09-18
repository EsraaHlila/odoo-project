from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_status = fields.Selection([
        ('pending', 'En cours'),
        ('sent', 'Envoyé'),
        ('closed', 'Fermé')
    ], string="Statut de commande", default='pending')

@api.onchange('partner_id', 'order_line')
def apply_children_discount(self):
    for order in self:
        if order.partner_id.children_count and order.partner_id.children_count >= 2:
            for line in order.order_line:
                line.discount = 10  # Apply 10% discount
        else:
            for line in order.order_line:
                line.discount = 0
