# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    slack_shipping_expedition_incidence = fields.Boolean( 
        string='Recibir incidencias de expediciones'
    )