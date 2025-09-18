from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Toggle: Individual or Company
    company_type = fields.Selection([
        ('person', 'Individual'),
        ('company', 'Company')],
        string='Company Type',
        default='person')

    # Contact person fields
    contact_name = fields.Char(string="Nom du contact")
    contact_email = fields.Char(string="Email du contact")
    contact_phone = fields.Char(string="Téléphone du contact")
    contact_function = fields.Char(string="Fonction du contact")

    # Entreprise fields
    entreprise_name = fields.Char(string="Nom de l’entreprise")
    entreprise_type = fields.Selection([
        ('sa', 'Société Anonyme'),
        ('sarl', 'SARL'),
        ('sasu', 'SASU'),
        ('other', 'Autre')
    ], string="Type d’entreprise")
    registration_number = fields.Char(string="Numéro d’enregistrement")
    website = fields.Char(string="Site Web")

