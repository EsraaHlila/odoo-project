from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class TextBeeSMS(models.Model):
    _name = 'sms.textbee'
    _description = 'TextBee SMS Integration'

    name = fields.Char('Reference', default='New', required=True)

    parent_recipients = fields.Many2many(
        comodel_name='unique.parent',
        string='Parent Recipients'
    )

    partner_recipients = fields.Many2many(
        comodel_name='res.partner',
        string='Partner Recipients'
    )

    recipient_numbers = fields.Text(
        'Recipient Numbers',
        help="Enter phone numbers separated by commas or new lines"
    )

    message = fields.Text('Message', required=True)
    sender_id = fields.Char('Sender ID', default='Khotoua')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ], string='Status', default='draft')
    response_data = fields.Text('API Response')
    sent_date = fields.Datetime('Sent Date')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sms.textbee') or 'New'
        return super().create(vals)

    def action_send_sms(self):
        self.ensure_one()
        
        config = self.env['ir.config_parameter'].sudo()
        api_key = config.get_param('textbee_api_key', '')
        device_id = config.get_param('textbee_sender_id', '')
        if not api_key or not device_id:
            raise UserError("TextBee API credentials not configured! Please set them in Settings.")
        
        # Collect all numbers from parents, partners, and manual entry
        numbers = []
        numbers += [p.phone_number for p in self.parent_recipients if p.phone_number]
        numbers += [p.phone for p in self.partner_recipients if p.phone]

        if self.recipient_numbers:
            for line in self.recipient_numbers.split('\n'):
                for num in line.split(','):
                    cleaned_num = num.strip()
                    if cleaned_num:
                        numbers.append(cleaned_num)
        
        if not numbers:
            raise UserError("No valid phone numbers provided!")

        try:
            url = f"https://api.textbee.dev/api/v1/gateway/devices/{device_id}/send-sms"
            payload = {
                "recipients": numbers,
                "message": self.message,
                "senderId": self.sender_id
            }
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response_data = response.json()
            success = response_data.get("data", {}).get("success", False)
            message_text = response_data.get("data", {}).get("message", "Unknown response")

            self.write({
                'status': 'sent' if success else 'failed',
                'response_data': json.dumps(response_data, indent=2),
                'sent_date': fields.Datetime.now()
            })

            if success:
                _logger.info(f"SMS sent successfully to {len(numbers)} recipients")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message_text,
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                _logger.error(f"TextBee API error: {response_data}")
                raise UserError(f"Failed to send SMS: {message_text}")
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Network error: {str(e)}")
            self.write({'status': 'failed', 'response_data': f"Network error: {str(e)}"})
            raise UserError(f"Network error: {str(e)}")
        except Exception as e:
            _logger.error(f"Unexpected error: {str(e)}")
            self.write({'status': 'failed', 'response_data': f"Unexpected error: {str(e)}"})
            raise UserError(f"Unexpected error: {str(e)}")
    
    
    
    def action_load_all_parents(self):
        parents = self.env['unique.parent'].search([])
        if not parents:
            raise UserError("No parents found in the system.")
        self.parent_recipients = [(6, 0, parents.ids)]

    def action_load_all_partners(self):
        partners = self.env['res.partner'].search([('phone','!=',False)])
        if not partners:
            raise UserError("No partners with phone numbers found.")
        self.partner_recipients = [(6, 0, partners.ids)]



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    textbee_api_key = fields.Char('TextBee API Key', config_parameter='textbee_api_key')
    textbee_sender_id = fields.Char('TextBee Device ID', config_parameter='textbee_sender_id')

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('textbee_api_key', self.textbee_api_key)
        self.env['ir.config_parameter'].set_param('textbee_sender_id', self.textbee_sender_id)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            textbee_api_key=self.env['ir.config_parameter'].get_param('textbee_api_key', ''),
            textbee_sender_id=self.env['ir.config_parameter'].get_param('textbee_sender_id', ''),
        )
        return res
