# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    slack_shipping_expedition_incidence = fields.Boolean( 
        string='Recibir incidencias de expediciones'
    )