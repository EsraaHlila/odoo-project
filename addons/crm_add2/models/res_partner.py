from odoo import models, fields, api, _
import logging
import re

_logger = logging.getLogger(__name__)



#from   a_company_as_partner
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

    #support_agent_id = fields.Many2one('res.users', string="Agent de support")
    #internal_note = fields.Text(string="Note interne")
    #children_count = fields.Integer(string="Nombre d'enfants")
    #child_name = fields.Char(string="Nom Et Prenom de l'enfant")
    #grade = fields.Selection(
     #   [('1st', '1st grade'), ('2nd', '2nd grade'), ('3rd', '3rd grade'), ('4th', '4th grade'), ('5th', '5th grade'), ('6th', '6th grade')],
      #  string="Child's grade",
       # required=True
    #)
    #lead_state = fields.Char(string="Statut de lead")
    #school = fields.Char(string="Ecole")


    def _normalize_phone(self, phone):
        """Normalize phone numbers by removing all non-digit characters"""
        if not phone:
            return None
        return re.sub(r'[^\d+]', '', str(phone))

    @api.model
    def create(self, vals):
        # Skip merge for special cases
        if self._context.get('no_merge'):
            return super().create(vals)

        # Normalize phone numbers
        phone = self._normalize_phone(vals.get('phone'))
        mobile = self._normalize_phone(vals.get('mobile'))
        
        _logger.debug("Creating partner with phone: %s, mobile: %s", phone, mobile)

        # Search for existing partners
        domain = []
        if phone:
            domain.append(('phone', '=', phone))
        if mobile:
            domain.append(('mobile', '=', mobile))
        
        if not domain:
            return super().create(vals)

        # Combine conditions with OR if both exist
        if len(domain) > 1:
            domain = ['|'] + domain

        existing = self.search(domain, limit=1)
        if not existing:
            return super().create(vals)

        _logger.info("Merging duplicate contact. Existing: %s, New data: %s", existing.name, vals)

        # Prepare update values
        update_vals = {}
        for field, value in vals.items():
            if (field in self._fields and 
                value and 
                not existing[field] and 
                field not in ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')):
                update_vals[field] = value

        if update_vals:
            existing.with_context(no_merge=True).write(update_vals)
            existing.message_post(
                body=_("Contact automatically updated with new information from duplicate entry: %s") % 
                     ', '.join(update_vals.keys())
            )

        return existing
        

#from  a_company_as_partner
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        # Force default selection to "person" (individual)
        defaults['company_type'] = 'person'
        return defaults