'''from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_tag = fields.Selection([
        ('pending', 'En cours'),
        ('sent', 'Envoyé'),
        ('closed', 'Fermé')
    ], string="Statut de commande", default='pending')

    @api.onchange('partner_id', 'order_line')
    def apply_children_discount(self):
        for order in self:
            if order.partner_id.children_count and order.partner_id.children_count >= 2:
                for line in order.order_line:
                    line.discount = 10  #10% de remise
            else:
                for line in order.order_line:
                    line.discount = 0'''

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_tag = fields.Selection([
        ('pending', 'En cours'),
        ('sent', 'Envoyé'), 
        ('closed', 'Fermé')
    ], string="Statut de commande", default='pending')

    #@api.onchange('partner_id')
#    def _onchange_partner_id_apply_discount(self):
 #       """Apply discount when partner changes"""
  #      for order in self:
   #         discount = 10 if order.partner_id.children_count >= 2 else 0
    #        for line in order.order_line:
     #           line.discount = discount

#    @api.model
 #   def create(self, vals):
  #      """Apply discount when order is created"""
   #     order = super().create(vals)
    #    if order.partner_id.children_count >= 2:
#            order.order_line.write({'discount': 10})
 #       return order

 #   def write(self, vals):
  #      """Apply discount when partner is changed on existing order"""
   #     res = super().write(vals)
    #    if 'partner_id' in vals:
     #       for order in self:
      #          discount = 10 if order.partner_id.children_count >= 2 else 0
       #         order.order_line.write({'discount': discount})
        #return res
