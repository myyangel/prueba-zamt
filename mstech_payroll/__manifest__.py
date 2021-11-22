# -*- coding: utf-8 -*-

{
    'name': 'Odoo',
    'version': '14.0.1.0.0',
    'author': 'Mouse Technologies',
    'category': 'Accounting & Finance',
    'summary': 'Módulo de personalizaciones',
    'license': 'LGPL-3',
    'website': 'https://www.mstech.pe',
    'depends': [
        'hr',
        'hr.payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/l10n_pe_uit_year_views.xml',
        'report/report_hr_contract.xml',
        'report/report_hr_payslip.xml',
    ],   
    'installable': True,
    'sequence': 1,
}
