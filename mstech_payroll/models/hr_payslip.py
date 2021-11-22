# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    uit = fields.Float(string='Monto de la UIT', default=-1)
    monto_quinta_actual = fields.Float(string='Monto Actual de Renta de Quinta', compute='_compute_monto_quinta_actual', store=False, readonly=False)

    cts = fields.Float(string='Monto CTS', compute='_comp_calculo_benefits', store=False, readonly=False)
    grati = fields.Float(string='Gratificación', compute='_comp_calculo_benefits', store=False, readonly=False)
    bono = fields.Float(string='Bonificación', compute='_comp_calculo_benefits', store=False, readonly=False)

    remun_fam = fields.Float(string='Remuneración Familiar', compute='_comp_calculo_benefits', store=False, readonly=False)
    afp_aporte = fields.Float(string='AFP Aporte', compute='_comp_calculo_benefits', store=False, readonly=False)
    afp_prima = fields.Float(string='AFP Prima', compute='_comp_calculo_benefits', store=False, readonly=False)
    afp_comision = fields.Float(string='AFP Comsion', compute='_comp_calculo_benefits', store=False, readonly=False)
    essalud = fields.Float(string='EsSalud', compute='_comp_calculo_benefits', store=False, readonly=False)

    vales_ley = fields.Float(string='Vales Ley 28051', readonly=False)
    rem_vac_ad = fields.Float(string='Remuneración Vacacional', readonly=False)
    vac_ad = fields.Float(string='Adelanto Vacaciones', readonly=False)
    cuota_pres_adm = fields.Float(string='Cuota Prestamo Adm.', readonly=False)
    cuota_pres_viv = fields.Float(string='Cuota Prestamo Viv.', readonly=False)
    essalud_vida = fields.Float(string='EsSalud + Vida', readonly=False)
    prim_seg_med = fields.Float(string='Prima Seg. Medico', readonly=False)
    vale_consumo = fields.Float(string='Vale Consumo', readonly=False)
    essalud_aporte = fields.Float(string='Aporte EsSalud', readonly=False)
    seguro_vida = fields.Float(string='Seguro Vida Ley', readonly=False)
    seg_acc_pers = fields.Float(string='Seg. Acc. Personales', readonly=False)


    def _comp_calculo_benefits(self) :
        payslip_now = self.date_to
        payslip_year = payslip_now.year
        contract_now = self.contract_id.first_contract_date

        for record in self :
            if contract_now and (payslip_year == contract_now.year) :
                meses_trabajados = payslip_now.month - contract_now.month +1
    
                if meses_trabajados < 6:
                    devengado_geral= meses_trabajados/6
                else:
                    devengado_geral = 1

                if contract_now.month <= 5:
                    devengado_cts = meses_trabajados/5
                elif contract_now.month <= 11:
                    devengado_cts = meses_trabajados/6
            else:
                devengado_geral = 1
                devengado_cts = 1

            #REMUN FAM
            if self.employee_id.children != 0:
                calculo_remun_fam = 93
            else:
                calculo_remun_fam = 0

            record.remun_fam = calculo_remun_fam
            
            #INGRESOS
            ingresos = self.contract_id.wage + calculo_remun_fam

            #DESCUENTOS
            descuentos = 0

            # GRATI Y BONO
            if payslip_now.month == 7 or payslip_now.month == 12:
                calculo_grati = (ingresos-descuentos)*(devengado_geral)
            else:
                calculo_grati = 0

            record.grati = calculo_grati
            record.bono = calculo_grati * 0.09


            #CTS
            if payslip_now.month == 5 or payslip_now.month == 11:
                calculo_cts = (ingresos-descuentos)*(devengado_cts)
            else:
                calculo_cts = 0

            record.cts = calculo_cts

            #AFP
            record.afp_aporte = (ingresos-descuentos)*self.employee_id.percent_aporte
            record.afp_prima = (ingresos-descuentos)*self.employee_id.percent_prima
            record.afp_comision = (ingresos-descuentos)*self.employee_id.percent_comision

            #ESSALUD
            record.essalud = (ingresos-descuentos)*0.09
    



    def comp_renta_quinta_anual(self) :
        #self.ensure_one()
        payslip_now = self.date_to
        payslip_year = payslip_now.year
        contract_now = self.contract_id.date_start
        contract_year = contract_now and contract_now.year or (payslip_year - 1)
        months = 13
        if contract_now and (payslip_year == contract_year) :
            if contract_now.month <= 7 :
                months = payslip_now.month - contract_now.month + 1 + 1
            else :
                months = payslip_now.month - contract_now.month + 1 + 0.5
        uit = self.uit
        if (not uit) or (uit <= 0) :
            uit = self.env['l10n_pe.uit.year'].sudo().search([('year','=',payslip_year)], limit=1).uit or 4400
        amount_base = ((self.contract_id.wage or 950) * months) - (7 * uit)
        amount_year = amount_base / uit
        if amount_year <= 0 :
            amount_year = 0
        elif amount_year <= 5 :
            amount_year = amount_base  * 0.08
        elif amount_year <= 20 :
            amount_base = amount_base - (5*uit)
            amount_year = amount_base * 0.14
        elif amount_year <= 35 :
            amount_base = amount_base - (20*uit)
            amount_year = amount_base * 0.17
        elif amount_year <= 45 :
            amount_base = amount_base - (35*uit)
            amount_year = amount_base * 0.30
        return amount_year

    def _compute_monto_quinta_actual(self) :
        for record in self :
            monto_quinta_actual = 0
            year_payslip = record.date_to or datetime.date.today()
            enero = datetime.date(year_payslip.year, 1, 1)
            diciembre = datetime.date(year_payslip.year, 12, 31)
            year_payslips = [
                ('slip_id.employee_id','=',record.employee_id.id),
                ('slip_id.date_from','>=',str(enero)),
                ('slip_id.date_to','<=',str(diciembre)),
                ('slip_id','!=',record.id),
                ('salary_rule_id.category_id.code','=','QUINTA'),
            ]
            year_payslips = self.env['hr.payslip.line'].search(year_payslips)
            monto_quinta_actual = sum(year_payslips.mapped('amount'))
            monto_quinta_actual = record.comp_renta_quinta_anual() - monto_quinta_actual
            monto_quinta_actual = monto_quinta_actual / (13 - year_payslip.month)
            record.monto_quinta_actual = monto_quinta_actual

    def compute_sheet(self) :
        res = self.env['l10n_pe.uit.year'].sudo()
        for record in self :
            year = (record.date_to or fields.Date.today()).year
            record.uit = res.search([('year','=',year)], limit=1).uit or 4400
        res = super().compute_sheet()
        return res

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    @api.model
    def _get_default_rule_ids(self):
        rules = super._get_default_rule_ids()

        rules.write ([
            (0, 0, {
                'name': 'CTS',
                'sequence': 4,
                'code': 'CTS',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = payslip.cts',
            }),
            (0, 0, {
                'name': 'Gratificacion',
                'sequence': 5,
                'code': 'GRT',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = payslip.grati',
            }),
            (0, 0, {
                'name': 'Sistema de Pensiones',
                'sequence': 6,
                'code': 'SNP',
                'category_id': self.env.ref('hr_payroll.DED').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = payslip.afp_prima + payslip.afp_comision + payslip.afp_aporte',
            }),
            (0, 0, {
                'name': 'Renta de quinta',
                'sequence': 7,
                'code': 'R5ta',
                'category_id': self.env.ref('hr_payroll.DED').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = payslip.monto_quinta_actual',
            })
        ])

        return rules
