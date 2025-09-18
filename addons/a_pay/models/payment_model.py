from odoo import models, fields, api

class UniquePayment(models.Model):
    _name = 'unique.payment'
    _description = 'Unique Payment Model'
    _rec_name = 'parent_name'
    
    parent_name = fields.Char(string=" Last & First Name", required=True)
    parent_phone = fields.Char(string="Phone Number", required=True)
    billing_address = fields.Char(string='Billing Address', required=True)
    payment_type = fields.Selection([('online','En Ligne'),('cash','Cash Sur Place')],string='Payment Type',required=True)
    discount_code = fields.Char(string='Discount Code')
    code = fields.Char(string='Payment Code')  #default='New'
    amount = fields.Float(string='Amount', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed'),
    ], string='Status', default='draft')
    package_id = fields.Many2one('unique.package', string="Package")
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('unique.payment') or 'New'
        return super().create(vals)

    @api.model
    def _init_sequence(self):
        """Initialize the sequence if it doesn't exist"""
        if not self.env['ir.sequence'].search([('code', '=', 'unique.payment')]):
            self.env['ir.sequence'].create({
                'name': 'Payment Sequence',
                'code': 'unique.payment',
                'prefix': 'PAY-',
                'padding': 5,
            })