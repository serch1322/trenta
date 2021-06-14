# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ServicioaFactura(models.Model):
    _inherit = ['fleet.vehicle.log.services']

    # state = fields.Selection([('borrador','Borrador'),('facturado','Facturado')],string="Estado",default="borrador",copy=False)
    ubicacion = fields.Selection([('interno','Interno'),('externo','Externo')],string="Ubicacion de Servicio")
    mecanico = fields.Many2one('res.partner', string="Mecanico", required=True)
    def crear_factura_servicio(self):
        self.state = 'facturado'
        self.ensure_one()
        factu_prov = self.env['account.move']
        valores_factu_prov = {}
        valores_factu_prov.update({
            'partner_id': self.vendor_id.id,
            'invoice_date': self.date,
            'ref': self.inv_ref,
            'type': 'in_invoice',
        })
        lista_factu = []
        if self.cost_ids:
            for linea in self.cost_ids:
                if linea.cost_subtype_id:
                    lineas_factu = {
                        'name': linea.cost_subtype_id.name,
                        'quantity': 1,
                        'price_unit': linea.amount,
                    }
                    lista_factu.append((0, 0, lineas_factu))
        if lista_factu:
            valores_factu_prov.update({
                'invoice_line_ids': lista_factu,
            })
        factura_creada = factu_prov.create(valores_factu_prov)

