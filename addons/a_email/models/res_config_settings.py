from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    textbee_api_key = fields.Char(
        string="TextBee API Key",
        config_parameter='textbee_api_key'
    )
    textbee_device_id = fields.Char(
        string="TextBee Device ID",
        config_parameter='textbee_device_id'
    )