# -*- coding: utf-8 -*-

{
    'name': 'Variables de servicio',
    'author': 'ITReingenierias',
    'summary': 'Agregar variables de servicio',
    'version': '1.0',
    'data': [
        'security/ir.model.access.csv',
        'views/modulo_variables.xml',
        'views/variables_views.xml',
        'data/data.xml',
    ],
    'depends': [
        'sale',
        'base',
    ],
}