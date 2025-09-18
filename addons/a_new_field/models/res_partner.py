from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Add your custom fields here
    example_field1 = fields.Char(string="Example Field 1")
    example_field2 = fields.Integer(string="Example Field 2")
    example_selection = fields.Selection(
        selection=[('option1', 'Option 1'), ('option2', 'Option 2')],
        string="Example Selection"
    )