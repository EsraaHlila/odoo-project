from odoo import models, fields, api
from datetime import date

class UniqueChild(models.Model):
    _name = 'unique.child'
    _description = 'Unique child Model'
    _rec_name = 'full_name'
    
    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True)
    
    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = (rec.first_name or '') + " " + (rec.last_name or '')
    
    birth_date = fields.Date(string='Birth Date', required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    moyenne = fields.Float(string="Moyenne", required=True)
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender",
        required=True
    )
    school = fields.Char(string="School")
    niveauId = fields.Char(string="Grade")
    parent_id = fields.Many2one(
        comodel_name='unique.parent',
        string='Parent',
        required=True,
        ondelete='cascade'
    )
    code = fields.Char(string="Code")
    
    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                record.age = today.year - record.birth_date.year - (
                    (today.month, today.day) < 
                    (record.birth_date.month, record.birth_date.day)
                )
            else:
                record.age = 0
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.first_name or ''} {record.last_name or ''}".strip()
            result.append((record.id, name))
        return result
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):  # if no code is provided
            vals['code'] = self.env['ir.sequence'].next_by_code('unique.child') or 'New'
        return super().create(vals)

    @api.model
    def _init_sequence(self):
        """Initialize the sequence if it doesn't exist"""
        if not self.env['ir.sequence'].search([('code', '=', 'unique.child')]):
            self.env['ir.sequence'].create({
                'name': 'child Sequence',
                'code': 'unique.child',
                'prefix': 'COM-',
                'padding': 5,
            })