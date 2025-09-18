from odoo import models, fields, api
from datetime import date

class UniqueParent(models.Model):
    _name = 'unique.parent'
    _description = 'Unique parent Model'
    _rec_name = 'full_name'
    
    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True)
    supabase_id = fields.Integer(string="Supabase ID", readonly=False, index=True)
    
    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = (rec.first_name or '') + " " + (rec.last_name or '')

    birth_date = fields.Date(string='Birth Date', required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    phone = fields.Char(string="Phone Number")
    address = fields.Char(string="Address", required=True)
    email = fields.Char(string="Email Address")
    
    children_count = fields.Integer(
    string="Children Count",
    compute="_compute_children_count",
    store=True,
    readonly=False
)
    lead_state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('customer', 'Customer'),
        ('lost', 'Lost')
    ], string='Lead State', default='prospect')

    @api.depends('child_id')
    def _compute_children_count(self):
        for rec in self:
            rec.children_count = len(rec.child_id)

    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender",
        required=True
    )
    activee = fields.Boolean(string='Is Active')
    child_id = fields.One2many(
        comodel_name='unique.child',
        inverse_name='parent_id',
        string="Children"
    )
    code = fields.Char(string="Code")
    
    # --- NEW FIELD FOR GRAPH/PIVOT ---
    active_display = fields.Selection(
        [('active', ''), ('inactive', '')],
        string='Active Status',
        compute='_compute_active_display',
        store=True
    )

    #@api.depends('activee')
    #def _compute_active_display(self):
        #for rec in self:
         #   rec.active_display = 'active' if rec.activee else 'inactive'
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
            vals['code'] = self.env['ir.sequence'].next_by_code('unique.parent') or 'New'
        return super().create(vals)


    @api.model
    def _init_sequence(self):
        """Initialize the sequence if it doesn't exist"""
        if not self.env['ir.sequence'].search([('code', '=', 'unique.parent')]):
            self.env['ir.sequence'].create({
                'name': 'parent Sequence',
                'code': 'unique.parent',
                'prefix': 'COM-',
                'padding': 5,
            })
