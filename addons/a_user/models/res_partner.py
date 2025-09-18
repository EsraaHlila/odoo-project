from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        selection=[('person', 'Individual')],
        default='person',
        string="Company Type"
    )
    



'''def create(self, vals):
    if 'company_type' not in vals:
        vals['company_type'] = 'person'
    return super().create(vals)'''




