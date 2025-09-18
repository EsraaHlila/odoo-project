from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class Email_send(models.Model):
    _name = 'email.send'
    _description = 'Email Integration'

    name = fields.Char('Reference', default='New', required=True)

    partner_recipients = fields.Many2many(
        comodel_name='res.partner',
        string='Partner Recipients'
    )
    
    
    company_recipients = fields.Many2many(
        comodel_name='unique.company',
        string='Company Recipients'
    )

    recipient_emails = fields.Text(
        'Recipient Emails',
        help="Enter email addresses separated by commas or new lines"
    )

    subject = fields.Char('Subject', required=True)
    body = fields.Html('Message', required=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ], string='Status', default='draft')

    sent_date = fields.Datetime('Sent Date')
    response_data = fields.Text('System Response')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('email.send') or 'New'
        return super().create(vals)

    def action_send_email(self):
        self.ensure_one()

        # Collect all emails
        emails = []
        emails += [p.email for p in self.partner_recipients if p.email]

        if self.recipient_emails:
            for line in self.recipient_emails.split('\n'):
                for addr in line.split(','):
                    cleaned_email = addr.strip()
                    if cleaned_email:
                        emails.append(cleaned_email)

        if not emails:
            raise UserError("No valid email addresses provided!")

        try:
            # Use Odoo mail system
            Mail = self.env['mail.mail']
            mail_id = Mail.create({
                'subject': self.subject,
                'body_html': self.body,
                'email_to': ",".join(emails),
            })

            mail_id.send()

            self.write({
                'status': 'sent',
                'sent_date': fields.Datetime.now(),
                'response_data': f"Email sent to {len(emails)} recipients"
            })

            _logger.info(f"Email sent successfully to {len(emails)} recipients")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f"Email sent to {len(emails)} recipients",
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Email sending failed: {str(e)}")
            self.write({
                'status': 'failed',
                'response_data': f"Error: {str(e)}"
            })
            raise UserError(f"Failed to send email: {str(e)}")
    def action_load_all_partners(self):
        partners = self.env['res.partner'].search([('email','!=',False)])
        if not partners:
            raise UserError("No partners with emails found.")
        self.partner_recipients = [(6, 0, partners.ids)]
    
    
    def action_load_all_companies(self):
        companies = self.env['unique.company'].search([('email','!=',False)])
        if not companies:
            raise UserError("No companies with emails found.")
        self.company_recipients = [(6, 0, companies.ids)]
