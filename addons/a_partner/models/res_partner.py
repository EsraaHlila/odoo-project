from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Contact person fields
    contact_name = fields.Char(string="Nom du contact")
    contact_email = fields.Char(string="Email du contact")
    contact_phone = fields.Char(string="Téléphone du contact")
    contact_function = fields.Char(string="Fonction du contact")

    # Entreprise fields
    #entreprise_name = fields.Char(string="Nom de l’entreprise")
    #secteur = fields.Char(string="Secteur")
    #nombre_employes = fields.Integer(string="Nombre d’employés")
    #adresse_entreprise = fields.Char(string="Adresse de l’entreprise")
    #ville_entreprise = fields.Char(string="Ville")
    #pays_entreprise = fields.Char(string="Pays")

