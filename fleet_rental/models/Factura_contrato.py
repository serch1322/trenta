# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ContratoFactura(models.Model):
    _inherit = ['fleet.vehicle.log.contract']

    def crear_factura_contrato(self):
        self.state = 'open'
        self.ensure_one()
        factu_prov = self.env['account.move']
        valores_factu_prov = {}
        valores_factu_prov.update({
            'partner_id': self.insurer_id.id,
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

