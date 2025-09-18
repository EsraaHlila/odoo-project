from odoo import models, fields, api, SUPERUSER_ID
from datetime import date, timedelta

class UniquePackage(models.Model):
    _name = 'unique.package'
    _description = 'Unique Package Model'

    name = fields.Char(string="Name", required=True)
    price = fields.Integer(string="Price")
    validation_days = fields.Integer(string="Validation Days")
    description = fields.Text(string="Description")

    code = fields.Char(string="Code", required=True, default='New')

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('unique.package') or 'New'
        return super().create(vals)

    @api.model
    def _init_sequence(self):
        """Initialize the sequence if it doesn't exist"""
        sequence = self.env['ir.sequence'].search([('code', '=', 'unique.package')])
        if not sequence:
            self.env['ir.sequence'].create({
                'name': 'Package Sequence',
                'code': 'unique.package',
                'prefix': 'COM-',
                'padding': 5,
                'number_next': 1,
                'number_increment': 1,
            })
