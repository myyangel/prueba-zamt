# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class L10nPeUITYear(models.Model) :
    _name = 'l10n_pe.uit.year'
    _description = 'Valor Anual de la UIT'
    _order = 'year asc'

    year = fields.Integer(string='Año')
    uit = fields.Float(string='Monto de la UIT')

    @api.depends('year')
    def name_get(self) :
        return [(rec.id, 'UIT del año '+str(rec.year)) for rec in self]

