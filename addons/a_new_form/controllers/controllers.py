from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteFormController(http.Controller):

    @http.route('/website/opportunity-form', type='http', auth='public', website=True)
    def opportunity_form(self, **kw):
        return request.render('a_new_form.view_opportunity_form_page')

    @http.route('/website/contact-form', type='http', auth='public', website=True)
    def contact_form(self, **kw):
        return request.render('a_new_form.view_contact_form_page')

    @http.route('/crm/create', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def create_opportunity(self, **post):
        stage = request.env['crm.stage'].sudo().search([
            ('name', '=', 'Qualified')
        ], limit=1)

        request.env['crm.lead'].sudo().create({
            'name': post.get('name'),
            'email_from': post.get('email_from'),
            'phone': post.get('phone'),
            'partner_name': post.get('company'),
            'description': post.get('questions'),
            'stage_id': stage.id if stage else False,
            'type': 'opportunity'
        })

        # return request.redirect('/thank-you')

    @http.route('/contact/create', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def create_contact(self, **post):
        _logger.info("🔍 Received contact form POST data: %s", post)

        request.env['res.partner'].sudo().with_context(no_merge=True, skip_duplicate_check=True).create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'comment': f"{post.get('subject', '')}\n\n{post.get('questions', '')}"
        })

        return "<h1>Contact created!</h1>"

        # return request.redirect('/thank-you')
