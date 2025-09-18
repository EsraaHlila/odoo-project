from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SMSComposer(models.Model):
    _name = 'sms.composer'
    _description = 'SMS Message Composer'

    name = fields.Char(string='Description', required=False)
    recipient_numbers = fields.Text(string='Recipient Numbers', required=True, 
                                  help='Enter phone numbers, one per line')
    message = fields.Text(string='Message', required=True)
    provider_id = fields.Many2one('textbee.provider', string='SMS Provider', required=False,
                                domain=[('active', '=', True)],
                                default=lambda self: self._default_provider_id())

    @api.model
    def _default_provider_id(self):
        """Get the first active provider as default"""
        provider = self.env['textbee.provider'].search([('active', '=', True)], limit=1)
        return provider.id if provider else False

    def action_send_sms(self):
        """Send SMS to the specified numbers"""
        self.ensure_one()
        
        if not self.recipient_numbers.strip():
            raise UserError(_("Please enter at least one recipient number."))
        
        if not self.message.strip():
            raise UserError(_("Please enter a message to send."))
        
        if not self.provider_id:
            raise UserError(_("Please select an SMS provider."))
        
        numbers = [num.strip() for num in self.recipient_numbers.split('\n') if num.strip()]
        success_count = 0
        failed_numbers = []
        
        for number in numbers:
            try:
                self.provider_id.send_sms(number, self.message)
                success_count += 1
            except Exception as e:
                failed_numbers.append(f"{number} ({str(e)})")
        
        if failed_numbers:
            raise UserError(_("SMS sent to %d numbers. Failed for: %s", 
                            success_count, ", ".join(failed_numbers)))
        else:
            raise UserError(_("SMS successfully sent to %d numbers!", success_count))

    @api.model
    def send_sms_to_number(self, number, message):
        """Utility method to send SMS from anywhere in your code"""
        provider = self.env['textbee.provider'].search([('active', '=', True)], limit=1)
        if not provider:
            raise UserError(_("Please configure TextBee SMS provider first."))
        
        try:
            provider.send_sms(number, message)
            return True
        except Exception as e:
            raise UserError(_("Failed to send SMS: %s", e))