from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    support_agent_id = fields.Many2one('res.users', string="Agent de support")
    internal_note = fields.Text(string="Note interne")
    children_count = fields.Integer(string="Nombre d’enfants")

@api.model
def create(self, vals):
    phone = vals.get('phone')
    if phone:
        existing = self.search([('phone', '=', phone)], limit=1)
        if existing:
            # mise à jour de fields fer8in akahaw
            for field_name, value in vals.items():
                if field_name in self._fields and value and not existing[field_name]:
                    existing[field_name] = value

            existing.message_post(body="Ce contact a été fusionné automatiquement (basé sur le téléphone).")
            return existing

    # No existing match → create normally
    return super().create(vals)
