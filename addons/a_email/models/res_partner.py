from odoo import models, api, _
from odoo.exceptions import UserError

class UniqueParent(models.Model):
    _inherit = 'unique.parent'  # Replace with your actual model name if different

    def action_send_sms(self):
        """Send SMS to this unique parent"""
        if not self.phone:  # Replace with your actual phone field name
            raise UserError(_("This parent has no phone number set."))
        
        # Get the active TextBee configuration
        provider = self.env['textbee.provider'].search([('active', '=', True)], limit=1)
        if not provider:
            raise UserError(_("Please configure TextBee SMS provider first in Settings → Technical → TextBee SMS."))
        
        # You can create a wizard for message input, but for now let's use a fixed test message
        message = _("Hello from Odoo! Test SMS to parent.")
        
        try:
            provider.send_sms(self.phone, message)  # Replace with your actual phone field
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success"),
                    'message': _("SMS sent to %s", self.phone),  # Replace with your actual phone field
                    'type': 'success',
                    'sticky': False,
                }
            }
        except UserError as e:
            raise UserError(_("Failed to send SMS: %s", e))



    def action_send_test_sms(self):
        """Button to send test SMS to this partner"""
        self.ensure_one()
        self.send_sms_via_textbee(_("Test SMS from Odoo"))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success"),
                'message': _("Test SMS sent to %s", self.phone),
                'type': 'success',
                'sticky': False,
            }
        }





    def action_send_mass_sms(self):
        """Send mass SMS to selected unique parents"""
        if not self:
            raise UserError(_("Please select at least one parent to send SMS."))
        
        parents_without_phone = self.filtered(lambda p: not p.phone)  # Replace with your actual phone field
        if parents_without_phone:
            raise UserError(_("The following parents have no phone number: %s", 
                            ", ".join(parents_without_phone.mapped('name'))))
        
        provider = self.env['textbee.provider'].search([('active', '=', True)], limit=1)
        if not provider:
            raise UserError(_("Please configure TextBee SMS provider first."))
        
        # For mass SMS, you'd typically create a wizard for message input
        # For now, let's send a test message
        message = _("Hello from Odoo! Mass SMS test.")
        
        success_count = 0
        failed_parents = []
        
        for parent in self:
            try:
                provider.send_sms(parent.phone, message)  # Replace with your actual phone field
                success_count += 1
            except Exception:
                failed_parents.append(parent.name)
        
        if failed_parents:
            raise UserError(_("SMS sent to %d parents. Failed for: %s", 
                            success_count, ", ".join(failed_parents)))
        else:
            raise UserError(_("SMS successfully sent to %d parents!", success_count))