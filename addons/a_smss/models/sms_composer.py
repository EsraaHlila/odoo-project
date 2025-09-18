from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SMSSimple(models.Model):
    _name = 'sms.simple'
    _description = 'Simple SMS Sender'

    numbers = fields.Text(string='Phone Numbers', required=True, help='One number per line')
    message = fields.Text(string='Message', required=True)

    def action_send_sms(self):
        """Simple SMS sending with direct API call"""
        if not self.numbers.strip():
            raise UserError(_("Please enter at least one phone number."))
        
        if not self.message.strip():
            raise UserError(_("Please enter a message to send."))
        
        # DIRECT API CALL - Replace with your actual TextBee details
        api_key = "73ef8f78-8af0-440a-a8e9-7e0f685033e3"  # ← REPLACE THIS
        api_url = "https://api.textbee.dev/api/v1/send"  # ← REPLACE THIS
        
        numbers = [num.strip() for num in self.numbers.split('\n') if num.strip()]
        success_count = 0
        failed_numbers = []
        
        for number in numbers:
            try:
                # Direct API call to TextBee
                payload = {
                    "api_key": api_key,
                    "to": number,
                    "message": self.message
                }
                headers = {"Content-Type": "application/json"}
                
                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    success_count += 1
                    _logger.info(f"SMS sent successfully to {number}")
                else:
                    error_msg = f"API Error: {response.status_code} - {response.text}"
                    failed_numbers.append(f"{number} ({error_msg})")
                    _logger.error(f"SMS failed to {number}: {error_msg}")
                    
            except Exception as e:
                error_msg = str(e)
                failed_numbers.append(f"{number} ({error_msg})")
                _logger.error(f"SMS failed to {number}: {error_msg}")
        
        if failed_numbers:
            raise UserError(_("SMS sent to %d numbers. Failed for: %s", success_count, ", ".join(failed_numbers)))
        else:
            raise UserError(_("SMS successfully sent to %d numbers!", success_count))