from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    droit_de_timbre = fields.Monetary(
        string="Droit de Timbre",
        compute="_compute_droit_de_timbre",
        store=True,
        currency_field="currency_id"
    )

    amount_total_with_stamp = fields.Monetary(
        string="Total TTC",
        compute="_compute_droit_de_timbre",
        store=True,
        currency_field="currency_id"
    )

    @api.depends('amount_total', 'amount_tax')
    def _compute_droit_de_timbre(self):
        for move in self:
            # Apply stamp only on customer invoices and refunds
            if move.is_invoice(include_receipts=True) and move.move_type in ('out_invoice', 'out_refund'):
                move.droit_de_timbre = 1.0
            else:
                move.droit_de_timbre = 0.0

            move.amount_total_with_stamp = move.amount_total + move.droit_de_timbre






















#class AccountMove(models.Model):
 #   _inherit = 'account.move'
#
 #   droit_de_timbre = fields.Monetary(
  #      string="Droit de Timbre",
  #      currency_field='currency_id',
   #     default=1.0,
   #     help="Tunisian stamp duty, usually 1 TND per invoice."
    #)

    # No _compute_amount override! We just keep this as a separate field.
#    @api.depends('line_ids.debit', 'line_ids.credit', 'line_ids.currency_id', 
 #                'line_ids.amount_currency')
  #  def _compute_amount(self):
        # First call the original computation
   #     super()._compute_amount()
        
        # Then add 1 TND to the total amounts for all invoices
    #    for move in self:
     #       if move.is_invoice(True):
      #          sign = move.direction_sign
       #         move.amount_total += sign * 1.0  # Always add exactly 1 TND
        #        move.amount_total_signed = abs(move.amount_total) if move.move_type == 'entry' else -move.amount_total
         #       move.amount_total_in_currency_signed = abs(move.amount_total) if move.move_type == 'entry' else -(sign * move.amount_total)
    
    
    
    
#from odoo import fields, models, api

#class AccountMove(models.Model):
 #   _inherit = 'account.move'

  #  droit_de_timbre = fields.Monetary(
   #     string="Droit de Timbre",
    #    compute="_compute_droit_de_timbre",
#        store=True,
 #       currency_field='currency_id'
  #  )

   # @api.depends('amount_tax', 'amount_untaxed')
    #def _compute_droit_de_timbre(self):
     #   """Compute the fixed stamp duty if there is any taxable amount."""
      #  for move in self:
            # Apply only to customer invoices (not vendor bills or misc entries)
       #     if move.is_invoice(True):
                # Example: Apply 1.0 only if there is taxable amount
        #        move.droit_de_timbre = 1.0 if move.amount_tax > 0 or move.amount_untaxed > 0 else 0.0
         #   else:
          #      move.droit_de_timbre = 0.0

    #@api.depends('amount_untaxed', 'amount_tax', 'droit_de_timbre')
    #def _compute_amount_total_including_stamp(self):
     #   """
        #Extend Odoo's computed amount_total WITHOUT overriding _compute_amount
      #  """
      #  for move in self:
       #     move.amount_total += move.droit_de_timbre

               
    #amount_total_with_stamp = fields.Monetary(
    #string="Total TTC (Avec Timbre)",
    #compute="_compute_amount_total_with_stamp",
    #store=False,
    #currency_field='currency_id'
#)

 #   @api.depends('amount_total', 'droit_de_timbre')
  #  def _compute_amount_total_with_stamp(self):
   #     for move in self:
    #        move.amount_total_with_stamp = move.amount_total + move.droit_de_timbre

    
    
    
    
    
    
                
#    def action_post(self):
 #       for move in self:
  #          if move.is_invoice(True) and move.droit_de_timbre and move.state == 'draft':
   #             # Just use the journal's default account for testing
    #            self.env['account.move.line'].create({
     #               'move_id': move.id,
      #              'account_id': move.journal_id.default_account_id.id,
       #             'name': 'Droit de Timbre',
        #            'debit': 1.0 if move.move_type in ('in_invoice', 'out_refund') else 0.0,
         #           'credit': 1.0 if move.move_type in ('out_invoice', 'in_refund') else 0.0,
          #          'partner_id': move.partner_id.id,
           #         'exclude_from_invoice_tab': True,
           #     })
    
        #return super().action_post()



#from odoo import models


 #   
    # Do NOT redefine partner_id, just inherit to keep it standard
    # No custom fields, no compute, no overrides
  #  pass
