# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class EntidadMatricula(models.Model):
    _inherit = ['fleet.vehicle']

    entidad = fields.Many2one('res.country.state', string="Entidad de Matricula")
    future_driver = fields.Many2many('res.partner', string="Conductores Aprobados", tracking=True, help='Next Driver of the vehicle',
                                       copy=False,
                                       domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    serie_motor = fields.Char(string="Numero de Serie Motor")
    numero_cilindros = fields.Float(string="Numero de Cilindros")
    seats = fields.Integer(string="Numero de Pasajeros", help='Number of seats of the vehicle')
    carga= fields.Float(string="Capacidad de Carga")
    categoria = fields.Many2one('car.category',string="Categoria de Vehiculo")
    tipo = fields.Selection(related='categoria.tipo')
    depr = fields.Selection([('total', 'Depreciación Total'), ('parcial', 'Depreciación Parcial')],string="Tipo de Depreciación",default=False)
    insurance_count = fields.Integer(compute="_compute_count_all", string="Seguro", store=True)
    tools_count = fields.Integer(compute="_compute_count_all", string="Accesorios/Aditamentos", store=True)

    def return_actions_to_open_seguro(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('state', '=', 'corriendo'), ('lineas_ids.car', '=', self.id)]
            )
            return res
        return False

    def return_actions_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:

            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('car', '=', self.id)]
            )
            return res
        return False

    def return_actions_to_open_venta_vehiculo(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        venta = self.env['venta.vehiculo']
        venta_creada = {}
        venta_creada.update({
            'name': self.model_id.id,
            'numero_bastidor': self.vin_sn,
        })
        activo_creado = venta.create(venta_creada)
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('fleet_rental.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('name', '=', self.model_id.id)]
            )
            return res
        return False

    def _compute_count_all(self):
        Odometer = self.env['fleet.vehicle.odometer']
        LogService = self.env['fleet.vehicle.log.services']
        LogContract = self.env['fleet.vehicle.log.contract']
        insurance = self.env['car.insurance']
        tools = self.env['car.tools']
        for record in self:
            record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.id)])
            record.service_count = LogService.search_count([('vehicle_id', '=', record.id)])
            record.contract_count = LogContract.search_count(
                [('vehicle_id', '=', record.id), ('state', '!=', 'closed')])
            record.history_count = self.env['fleet.vehicle.assignation.log'].search_count(
                [('vehicle_id', '=', record.id)])
            record.insurance_count = insurance.search_count(
                [('lineas_ids.car', '=', record.id), ('state', '=', 'corriendo')])
            record.tools_count = tools.search_count([('car', '=', record.id)])

    def depreciacion(self):
        self.ensure_one()
        activo = self.env['account.asset']
        valores_activo = {}
        valores_activo.update({
            'name': self.license_plate,
            'original_value': self.net_car_value,
            'acquisition_date': self.acquisition_date,
            'salvage_value': 0,
            'method': 'linear',
            'method_period': 1,
            'first_depreciation_date': date.today(),
            'company_id': 1,
            'account_asset_id': self.categoria.activo.id,
            'account_depreciation_id': self.categoria.amortizacion.id,
            'account_depreciation_expense_id': self.categoria.gasto.id,
            'journal_id': 3,
            'state': 'open',
        })
        if self.tipo == 'carga':
            valores_activo.update({
                'method_number': 48,
            })
        else:
            if self.depr == 'total':
                valores_activo.update({
                    'method_number': 1,
                })
            else:
                if self.net_car_value > '175000':
                    valores_activo.update({
                        'salvage_value': self.net_car_value - 175000,
                        'method_number': 48,
                    })
                elif self.net_car_value <= '175000':
                    valores_activo.update({
                        'salvage_value': 0,
                        'method_number': 48,
                    })
        activo_creado = activo.create(valores_activo)

class EntidadMatricula(models.Model):
    _inherit = ['fleet.vehicle.model']

    activo = fields.Many2one('account.account', string="Cuenta de Activo", required=True)
    amortizacion = fields.Many2one('account.account', string="Cuenta de Amortizacion", required=True)
    gasto = fields.Many2one('account.account', string="Cuenta de Gasto", required=True)

class ventaVehiculo(models.Model):
    _name = 'venta.vehiculo'
    _description = 'Venta'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    venta = fields.Selection([('sin', 'Sin Accesorios/Aditamentos'), ('con', 'Con Accesorios/Aditamentos')], string="Tipo de Venta", copy=False)
    name = fields.Many2one('fleet.vehicle',string="Vehículo", required=True, domain="[('insurance_count','=','0')]")
    numero_bastidor = fields.Char(string="Numero de Bastidor", required=True)

    def vender(self, cr, uid, ids, context=None):
        tools = self.env['car.tools'].search([])
        if self.venta == 'sin':
            for tool in tools:
                if tool.car == self.name.id:
                    tl_ids = tool.search(cr, uid, [('car', '=', self.name.id)], context=context)
                    tools.unlink(cr, uid, tl_ids, context=context)




