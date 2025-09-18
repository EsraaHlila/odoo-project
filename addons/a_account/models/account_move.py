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

    # Computed fields to override partner info for reports/email
    report_partner_name = fields.Char(string='Report Customer Name', compute='_compute_report_partner')
    report_partner_email = fields.Char(string='Report Customer Email', compute='_compute_report_partner')

    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        move = self.env['account.move'].browse(self._context.get('active_ids', []))
        if move and move.x_company_id:
            # assign the mail_partner_ids from the company
            res['mail_partner_ids'] = move.x_company_id.mail_partner_ids.ids
        return res
#    def _get_mail_values(self, res_ids):
 #       """Override the recipient email for invoice emails"""
  #      vals = super()._get_mail_values(res_ids)
   #     for rec in self:
    #        if rec.x_company_id and rec.mail_partner_ids:
                # set the recipient to the company email instead of dummy partner
     #           vals['email_to'] = rec.mail_partner_ids
      #  return vals
