#from odoo import models

#class AccountMove(models.Model):
 #   _inherit = 'account.move'
    # Do NOT redefine partner_id, just inherit to keep it standard
    # No custom fields, no compute, no overrides
    
    # models/account_move.py
    #pass

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_company_id = fields.Many2one('unique.company', string='Company Customer')

    @api.onchange('x_company_id')
    def _onchange_x_company_id(self):
        dummy_partner = self.env['res.partner'].browse(1)  # or use id: self.env['res.partner'].browse(1)
        if self.x_company_id:
            self.partner_id = dummy_partner
            
class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    x_company_id = fields.Many2one(
        comodel_name="unique.company",
        string="Company"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Prefill x_parent_id from the active invoice
        active_id = self.env.context.get('active_id')
        if active_id:
            invoice = self.env['account.move'].browse(active_id)
            res['x_company_id'] = invoice.x_company_id
        return res
