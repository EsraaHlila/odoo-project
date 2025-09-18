from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # Force default selection to "person" (individual)
        defaults['company_type'] = 'person'
        return defaults