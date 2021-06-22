# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _


class RentContract(models.Model):
    _name = 'car.insurance'
    _description = 'Seguros'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('lineas_ids.subtotal')
    def _obtener_totales(self):
        for insurance in self:
            total_concepts = 0.0
            for line in insurance.lineas_ids:
                total_concepts = total_concepts + line.subtotal
            insurance.total_concepts = total_concepts

    total_concepts = fields.Float(string="Total", compute="_obtener_totales", store=True)
    name = fields.Char(string="Numero de Poliza",  required =True)
    supplier = fields.Many2one('res.partner',string="Proveedor", required =True)
    siniestro = fields.Char(string="Reporte de Siniestros", required=True)
    atencion_clientes = fields.Char(string="Atención a Clientes", required=True)
    grua = fields.Char(string="Solicitar Grua o Asistencia Vial", required=True)
    invoice_date = fields.Date(string="Inicio de Poliza", required =True)
    end_date = fields.Date(string="Vencimiento Poliza", required =True)
    inciso = fields.Char(string="Inciso")
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, index=True)
    state = fields.Selection(
        [('nuevo', 'Nuevo'), ('corriendo', 'Corriendo'), ('terminado', 'Terminado'), ('cancelado', 'Cancelado')], string="Estado",
        default="nuevo", copy=False)
    lineas_ids = fields.One2many('line.car.insurance','asegurado',readonly=False)

    def accion_aprobado(self):
        self.state = 'corriendo'
        self.ensure_one()
        factu_prov = self.env['account.move']
        valores_factu_prov = {}
        valores_factu_prov.update({
         'partner_id': self.supplier.id,
         'invoice_date': self.invoice_date,
         'ref': self.name,
         'move_type': 'in_invoice',
        })
        lista_factu = []
        if self.lineas_ids:
         for linea in self.lineas_ids:
             if linea.car:
                 lineas_factu = {
                     'name': linea.car.license_plate,
                     'quantity': linea.qty,
                     'price_unit': linea.price,
                 }
                 lista_factu.append((0, 0, lineas_factu))
        if lista_factu:
         valores_factu_prov.update({
             'invoice_line_ids': lista_factu,
         })
        factura_creada = factu_prov.create(valores_factu_prov)

    def accion_cancelado(self):
        self.state = 'cancelado'

    def accion_borrador(self):
        self.state = 'nuevo'


    def vencimiento_seguro(self):
        today = fields.Date.today()
        seguros = self.env['car.insurance'].search([])
        for seguro in seguros:
            if seguro.state == 'corriendo'and seguro.end_date < today:
                seguro.state = 'terminado'


class CarrosAsegurados(models.Model):
    _name = 'line.car.insurance'

    @api.depends('qty', 'price')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price

    asegurado = fields.Many2one('car.insurance', string="Carros Asegurados")
    car = fields.Many2one('fleet.vehicle',string="Vehículo", required=True, domain="[('insurance_count','=','0')]")
    price = fields.Float(string="Costo de Poliza")
    qty = fields.Float(default= 1 ,string="Cantidad", readonly= True)
    subtotal = fields.Float(string="Subtotal", compute="_get_subtotal", store=True)
