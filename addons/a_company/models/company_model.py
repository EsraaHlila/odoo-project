from odoo import models, fields, api, SUPERUSER_ID
from datetime import date, timedelta

class UniqueCompany(models.Model):
    _name = 'unique.company'
    _description = 'Unique Company Model'

    name = fields.Char(string="Name", required=True)
    owner = fields.Many2one(
        comodel_name='res.partner',
        string="Contact"
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )
    # Add these fields to mimic res.partner behavior
#    commercial_partner_id = fields.Many2one(
 #       'res.partner',
  #      string='Commercial Entity',
   #     compute='_compute_commercial_partner_id',
   #     store=True
   # )
    is_company = fields.Boolean(string='Is a Company', default=True)
    parent_id = fields.Many2one('res.partner', string='Related Company')
    
    last_activity_date = fields.Date(
        string="Last Activity Date",
        required=True,
        default=fields.Date.context_today
    )
    days_since_last_activity = fields.Integer(
        string="Days Since Last Activity",
        compute="_compute_days_since_activity",
        store=True
    )
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email Address")
    lead_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('customer', 'Customer'),
        ('lost', 'Lost')
    ], string='Lead State', default='prospect')
    code = fields.Char(string="Code", required=True, default='New')
    
    @api.depends('last_activity_date')
    def _compute_days_since_activity(self):
        for record in self:
            if record.last_activity_date:
                today = date.today()
                last_activity = fields.Date.from_string(record.last_activity_date)
                record.days_since_last_activity = (today - last_activity).days
            else:
                record.days_since_last_activity = 0
    
#    @api.depends('owner')
 #   def _compute_commercial_partner_id(self):
  #      for record in self:
   #         if record.owner:
    #            # Use the owner's commercial_partner_id if available, otherwise the owner itself
     #           record.commercial_partner_id = record.owner.commercial_partner_id or record.owner
      #      else:
       #         record.commercial_partner_id = False