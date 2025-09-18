from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ugs = fields.Char(string="UGS")
