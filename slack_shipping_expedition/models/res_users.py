# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    slack_shipping_expedition_incidence = fields.Boolean( 
        string='Receive incidents of expeditions'
    )
