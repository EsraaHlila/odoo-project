from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_send_whatsapp(self):
        for lead in self:
            if lead.phone:
                message = f"Hello {lead.name}, we received your request!"
                whatsapp_url = f"https://wa.me/{lead.phone}?text={message}"
                return {
                    'type': 'ir.actions.act_url',
                    'name': 'WhatsApp',
                    'target': 'new',
                    'url': whatsapp_url,
                }

