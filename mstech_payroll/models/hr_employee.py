# -*- coding: utf-8 -*

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sist_pension = fields.Selection(selection=[('onp', 'ONP'),('hab', 'Habitat'),('int', 'Integra'),('pri', 'Prima'),('pro','Profuturo')], string='Sistema de pensiones')
    tipo_comision = fields.Selection(selection=[('fl', 'Flujo'),('mx', 'Mixta')], string='Tipo de comisión')
    percent_comision_total = fields.Float(string="Porcentaje de comisión", compute='_compute_comision', store=False, readonly=False)
    percent_comision = fields.Float(string="Comisión", compute='_compute_comision')
    percent_prima = fields.Float(string="Prima de Seguro", compute='_compute_comision')
    percent_aporte = fields.Float(string="Aporte Obligatorio", compute='_compute_comision')


    @api.depends('sist_pension', 'tipo_comision')
    def _compute_comision (self):
        comision = 0
        prima = 0.0174
        fondo = 0.1
        for record in self:
            if record.sist_pension == 'onp':
                comision = 0.13

            elif record.sist_pension == 'hab':
                if record.tipo_comision == 'fl':
                   comision = 0.0147
                elif record.tipo_comision == 'mx':
                   comision = 0.0023

            elif record.sist_pension == 'pri':
                if record.tipo_comision == 'fl':
                   comision = 0.0160
                elif record.tipo_comision == 'mx':
                   comision = 0.0018

            elif record.sist_pension == 'pro':
                if record.tipo_comision == 'fl':
                   comision = 0.0169
                elif record.tipo_comision == 'mx':
                   comision = 0.0028

            elif record.sist_pension == 'int':
                if record.tipo_comision == 'fl':
                   comision = 0.0155
                elif record.tipo_comision == 'mx':
                   comision = 0.00
            else:
               comision = 0

            if record.sist_pension == 'onp':
                record.percent_comision_total = comision
                record.percent_comision = comision
                record.percent_prima = 0
                record.percent_aporte = 0
            else:
                record.percent_comision_total = comision + prima + fondo
                record.percent_comision = comision
                record.percent_prima = prima
                record.percent_aporte = fondo

