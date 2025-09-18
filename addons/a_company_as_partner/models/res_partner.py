from odoo import models, fields, api

class AppUser(models.Model):
    _name = 'companiess'
    _description = 'for companies creation'
    _rec_name = 'name'

    name = fields.Char(required=True)
    email = fields.Char()
    phone = fields.Char()
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string="Linked CRM Contact", ondelete='set null')

    '''def action_sync_partner(self):
        for user in self:
            if not user.partner_id:
                user.partner_id = self.env['res.partner'].create({
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'is_company': False,
                })''' 
class ResPartner(models.Model):
    _inherit = 'res.partner'                
    
    
    @api.model
    def action_sync_partner(self):
        # This is just a placeholder logic for now
        # You can add your sync logic here
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Partner synced to CRM!',
                'type': 'success',
                'sticky': False,
            }
        }
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # Force default selection to "company"
        defaults['company_type'] = 'company'
        return defaults