# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technogies @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': 'Manejo de Renta de Vehiculos',
    'version': '15.0.1.0.0',
    'author': 'IT Reingenierias',
    'company': 'IT Reingenierias',
    'website': "https://www.itreingenierias.com",
    'depends': ['base', 'account', 'fleet', 'mail','account_asset','stock','purchase','sale'],
    'data': ['security/rental_security.xml',
             'security/ir.model.access.csv',
             'wizard/venta_de_vehiculo.xml',
             'views/car_rental_view.xml',
             'views/checklist_view.xml',
             'views/car_tools_view.xml',
             'views/insurance_view.xml',
             'views/licencia_contacto.xml',
             'views/factura_contrato.xml',
             'views/servicios.xml',
             'views/categoria_vehiculo.xml',
             'views/product_template.xml',
             'views/activos.xml',
             'views/tools_modelo.xml',
             'views/tools_categoria.xml',
             'views/vehiculo.xml',
             'views/facturacion.xml',
             'views/res_partner.xml',
             'reports/rental_report.xml',
             'data/fleet_rental_data.xml',
             'data/secuencias.xml',
             ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
