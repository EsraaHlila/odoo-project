from odoo import models, fields

class Lead(models.Model):
    _inherit = 'crm.lead'

    source = fields.Char(string='Source')
    notes = fields.Text(string='Lead Notes')
