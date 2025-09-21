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

    x_parent_id = fields.Many2one('unique.parent', string='Parent Customer')

    @api.onchange('x_parent_id')
    def _onchange_x_parent_id(self):
        dummy_partner = self.env['res.partner'].browse(41)  # or use id: self.env['res.partner'].browse(1)
        if self.x_parent_id:
            self.partner_id = dummy_partner
#from odoo import api, models

#from odoo import models, fields, api

#class AccountMoveSend(models.TransientModel):
 #   _inherit = 'account.move.send.wizard'

#    parent_id = fields.Many2one(
 #       'unique.parent',
  #      string="Parent Contact",
   #     help="Choose a parent contact to send this invoice to."
    #)

#    @api.onchange('parent_id')
 #   def _onchange_parent_id(self):
  #      """Auto-fill mail_partner_ids when selecting a parent."""
   #     if self.parent_id and self.parent_id.email:
            # Append to existing recipients
    #        existing_partners = self.mail_partner_ids
     #       parent_partner = self.env['res.partner'].search(
      #          [('email', '=', self.parent_id.email)], limit=1
       #     )
        #    if parent_partner:
         #       self.mail_partner_ids |= parent_partner



#class AccountMoveSendWizard(models.TransientModel):
 #   _inherit = "account.move.send.wizard"

  #  x_parent_id = fields.Many2one(
   #     comodel_name="unique.parent",
    #    string="Parent"
        #compute="_compute_parent_id"
    #)


class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    x_parent_id = fields.Many2one(
        comodel_name="unique.parent",
        string="Parent"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Prefill x_parent_id from the active invoice
        active_id = self.env.context.get('active_id')
        if active_id:
            invoice = self.env['account.move'].browse(active_id)
            res['x_parent_id'] = invoice.x_parent_id
        return res


#    @api.model
#    def default_get(self, fields_list):
#        """Prefill parent and recipients with the parent from the active invoice"""
 #       res = super().default_get(fields_list)
  #      active_id = self.env.context.get("active_id")
   #     if active_id:
    #        move = self.env["account.move"].browse(active_id)
     #       if move and move.x_parent_id:
                # Prefill our custom field with parent from invoice
                #res["x_parent_id"] = move.x_parent_id.id

                # Prefill email recipients (mail_partner_ids)
                # Get email from parent partner if available
      #          if move.x_parent_id.email:
       #             res["mail_partner_ids"] = [(6, 0, [move.x_parent_id.id])]
        #return res







  

#    def _compute_parent_id(self):
 #       for wizard in self:
  #          if wizard.move_id and wizard.move_id.x_parent_id:
   #             wizard.parent_id = wizard.move_id.x_parent_id.id
    #        else:
     #           wizard.parent_id = False






 






 

    #@api.depends('x_parent_id.full_name')
#    def _compute_name(self):
 #       for move in self:
  #          if move.x_parent_id and move.x_parent_id.full_name:
   #             move.name = move.x_parent_id.full_name
    #        elif not move.name:
                # Let Odoo generate the name as usual
     #           move.name = '/'
    
    
    
    
    
    
    
    
    
#    @api.depends('x_parent_id.full_name')
 #   def _compute_display_name(self):
  #      for move in self:
   #         if move.x_parent_id and move.x_parent_id.full_name:
    #            move.display_name = move.x_parent_id.full_name
     #       else:
      #          super(AccountMove, move)._compute_display_name()
    
    # Optional: If you want to also change the name field
#    name = fields.Char(compute='_compute_name')
    
 #   def _compute_name(self):
  #      for move in self:
   #         if move.x_parent_id and move.x_parent_id.full_name:
    #            move.name = move.x_parent_id.full_name
     #       else:
      #          move.name = move._get_invoice_computed_name()

    # Computed fields to override partner info for reports/email
    #report_partner_name = fields.Char(string='Report Customer Name', compute='_compute_report_partner')
    #report_partner_email = fields.Char(string='Report Customer Email', compute='_compute_report_partner')

    #@api.model
    #def default_get(self, fields):
     #   res = super(AccountMove, self).default_get(fields)
      #  move = self.env['account.move'].browse(self._context.get('active_ids', []))
       # if move and move.x_company_id:
            # assign the mail_partner_ids from the company
        #    res['mail_partner_ids'] = move.x_company_id.mail_partner_ids.ids
        #return res
#    def _get_mail_values(self, res_ids):
 #       """Override the recipient email for invoice emails"""
  #      vals = super()._get_mail_values(res_ids)
   #     for rec in self:
    #        if rec.x_company_id and rec.mail_partner_ids:
                # set the recipient to the company email instead of dummy partner
     #           vals['email_to'] = rec.mail_partner_ids
      #  return vals
