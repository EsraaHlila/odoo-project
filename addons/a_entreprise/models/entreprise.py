from odoo import models, fields

class Entreprise(models.Model):
    _name = 'entreprise.entreprise'
    _description = 'Entreprise'

    name = fields.Char(string="Nom de l’entreprise", required=True)
    secteur = fields.Char(string="Secteur")
    nombre_employes = fields.Integer(string="Nombre d’employés")
    adresse = fields.Char(string="Adresse")
    ville = fields.Char(string="Ville")
    pays = fields.Char(string="Pays")
    email = fields.Char(string="Email")  # <-- Add this
    phone = fields.Char(string="Téléphone")  # <-- Add this
    contact_function = fields.Char(string="Fonction du contact")  # <-- Add this

    contact_ids = fields.One2many('res.partner', 'entreprise_id', string="Contacts liés")
    

    
    


