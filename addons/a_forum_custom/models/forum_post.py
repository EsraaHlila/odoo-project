from odoo import models, fields

class ForumPost(models.Model):
    _inherit = 'forum.post'

    resolved_status = fields.Selection([
        ('non_resolu', 'Non Résolu'),
        ('resolu', 'Résolu')
    ], string="Statut de la question", default='non_resolu')
