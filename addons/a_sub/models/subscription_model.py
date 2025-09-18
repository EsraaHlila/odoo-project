from odoo import models, fields, api
from datetime import date

class UniqueSubscription(models.Model):
    _name = 'unique.subscription'
    _description = 'Unique Subscription Model'
    _rec_name = 'full_name'

    # --- Core fields ---
    parent_first_name = fields.Char(string="Parent's First Name", required=True)
    parent_last_name = fields.Char(string="Parent's Last Name", required=True)
    birth_date = fields.Date(string="Parent's Birth Date", required=True)
    full_name = fields.Char(string="Full Name", compute="_compute_full_name", store=True)
    
    @api.depends('parent_first_name', 'parent_last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = (rec.parent_first_name or '') + " " + (rec.parent_last_name or '')

    # Put 'female' first (this *may* help with palette order but is not guaranteed)
    gender = fields.Selection(
        [('female', 'Female'), ('male', 'Male')],
        string="Parent's Gender",
        required=True
    )

    child_first_name = fields.Char(string="Child's First Name", required=True)
    child_last_name = fields.Char(string="Child's Last Name", required=True)
    child_birth_date = fields.Date(string="Child's Birth Date", required=True)
    child_gender = fields.Selection(
        [('female', 'Female'), ('male', 'Male')],
        string="Child's Gender",
        required=True
    )

    activee = fields.Boolean(string='Is Active', default=True)
    ref = fields.Char(string='Subs Reference', required=True, default='New')
    #sale_order_id = fields.Many2one('sale.order', string="Sales Order")

    # --- Computed numeric ages (stored so they can be used as measures/group by) ---
    parent_age = fields.Integer(string="Parent Age", compute="_compute_parent_age", store=True)
    child_age = fields.Integer(string="Child Age", compute="_compute_child_age", store=True)

    @api.depends('birth_date')
    def _compute_parent_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                record.parent_age = (
                    today.year
                    - record.birth_date.year
                    - ((today.month, today.day) < (record.birth_date.month, record.birth_date.day))
                )
            else:
                record.parent_age = 0

    @api.depends('child_birth_date')
    def _compute_child_age(self):
        today = date.today()
        for record in self:
            if record.child_birth_date:
                record.child_age = (
                    today.year
                    - record.child_birth_date.year
                    - ((today.month, today.day) < (record.child_birth_date.month, record.child_birth_date.day))
                )
            else:
                record.child_age = 0

    # --- Stored selection for readable Active/Inactive in graphs/pivots (kept for search/grouping only) ---
    active_status = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive')],
        string='Active Status',
        compute='_compute_active_status',
        store=True
    )

    @api.depends('activee')
    def _compute_active_status(self):
        for rec in self:
            rec.active_status = 'active' if rec.activee else 'inactive'

    # --- Stored selections for readable age ranges in legends ---
    parent_age_range = fields.Selection(
        [
            ('under_30', 'Under 30'),
            ('30_40', '30–40'),
            ('over_40', 'Over 40'),
        ],
        string='Parent Age Range',
        compute='_compute_parent_age_range',
        store=True
    )

    child_age_range = fields.Selection(
        [
            ('under_5', 'Under 5'),
            ('5_10', '5–10'),
            ('over_10', 'Over 10'),
        ],
        string='Child Age Range',
        compute='_compute_child_age_range',
        store=True
    )

    @api.depends('parent_age')
    def _compute_parent_age_range(self):
        for rec in self:
            age = rec.parent_age or 0
            if age < 30:
                rec.parent_age_range = 'under_30'
            elif 30 <= age <= 40:
                rec.parent_age_range = '30_40'
            else:
                rec.parent_age_range = 'over_40'

    @api.depends('child_age')
    def _compute_child_age_range(self):
        for rec in self:
            age = rec.child_age or 0
            if age < 5:
                rec.child_age_range = 'under_5'
            elif 5 <= age <= 10:
                rec.child_age_range = '5_10'
            else:
                rec.child_age_range = 'over_10'

    # --- Helper integer for possible color mapping in JS (optional use) ---
    # 0 = female, 1 = male (keeps a predictable index on the record -> can be used by a JS patch)
    gender_color_index = fields.Integer(string='Gender Color Index', compute='_compute_gender_color_index', store=True)

    @api.depends('gender')
    def _compute_gender_color_index(self):
        for rec in self:
            if rec.gender == 'female':
                rec.gender_color_index = 0
            elif rec.gender == 'male':
                rec.gender_color_index = 1
            else:
                rec.gender_color_index = -1

    # --- Sequence for reference ---
    @api.model
    def create(self, vals):
        if vals.get('ref', 'New') == 'New':
            vals['ref'] = self.env['ir.sequence'].next_by_code('unique.subscription') or 'New'
        return super().create(vals)

    @api.model
    def _init_sequence(self):
        """Initialize the sequence if it doesn't exist"""
        if not self.env['ir.sequence'].search([('code', '=', 'unique.subscription')]):
            self.env['ir.sequence'].create({
                'name': 'Subscription Sequence',
                'code': 'unique.subscription',
                'prefix': 'SUB-',
                'padding': 5,
            })
