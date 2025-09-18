from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    child_name = fields.Char(string="Nom Et Prenom de l'enfant")
