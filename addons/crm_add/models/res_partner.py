from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    support_agent_id = fields.Many2one('res.users', string="Agent de support")
    internal_note = fields.Text(string="Note interne")
    children_count = fields.Integer(string="Nombre d’enfants")


    @api.model
    def create(self, vals):
        if 'phone' in vals and vals['phone']:
            existing = self.search([('phone', '=', vals['phone'])], limit=1)
            if existing:
                raise ValidationError("Ce client existe déjà avec ce numéro de téléphone.")
        return super().create(vals)
