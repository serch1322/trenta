# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ServicioaFactura(models.Model):
    _inherit = ['fleet.vehicle.log.services']

    state = fields.Selection([('borrador','Borrador'),('proceso','En Proceso'),('facturado','Facturado')],string="Estado",default="borrador",copy=False)
    ubicacion = fields.Selection([('interno','Interno'),('externo','Externo')],string="Ubicacion de Servicio")
    mecanico = fields.Many2one('res.partner', string="Mecanico")
    paga_cliente = fields.Boolean(string="Servicio pagado por Cliente",default=False)

    def validar(self):
        self.state = 'proceso'

    def crear_factura_servicio(self):
        if self.paga_cliente == True:
            self.state = 'facturado'
        else:
            self.state = 'facturado'
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
            lineas_factu = {
                'name': self.service_type_id.id,
                'quantity': 1,
                'price_unit': self.amount,
            }
            lista_factu.append((0, 0, lineas_factu))
            if lista_factu:
                valores_factu_prov.update({
                    'invoice_line_ids': lista_factu,
                })
            factura_creada = factu_prov.create(valores_factu_prov)

