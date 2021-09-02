# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServicioaFactura(models.Model):
    _inherit = ['fleet.vehicle.log.services']

    state = fields.Selection([('borrador','Borrador'),('proceso','En Proceso'),('facturado','Facturado')],string="Estado",default="borrador",copy=False)
    ubicacion = fields.Selection([('interno','Interno'),('externo','Externo')],string="Ubicacion de Servicio")
    mecanico = fields.Many2one('res.partner', string="Mecanico")
    paga_cliente = fields.Boolean(string="Servicio pagado por Cliente",default=False, copy=False)

    def validar(self):
        if self.paga_cliente == True:
            self.state = 'facturado'
        else:
            self.state = 'proceso'

    def unlink(self):
        if self.state == 'proceso' or self.state == 'facturado':
            raise UserError('No se puede eliminar ningun servicio facturado!')
        return models.Model.unlink(self)


    def crear_factura_servicio(self):
        mantenimiento = self.env['product.product'].search([("id", "=", "mantenimiento")])
        self.state = 'facturado'
        self.ensure_one()
        factu_prov = self.env['account.move']
        valores_factu_prov = {}
        valores_factu_prov.update({
            'partner_id': self.vendor_id.id,
            'invoice_date': self.date,
            'move_type': 'in_invoice',
        })
        lista_factu = []
        lineas_factu = {
            'product_id':mantenimiento,
            'name': self.description,
            'quantity': 1,
            'price_unit': self.amount,
            'tax_ids': mantenimiento.taxes_id,
            'product_uom_id': mantenimiento.uom_id.id,
            'account_id':mantenimiento.property_account_expense_id.id,
        }
        lista_factu.append((0, 0, lineas_factu))
        if lista_factu:
            valores_factu_prov.update({
                'invoice_line_ids': lista_factu,
            })
        factura_creada = factu_prov.create(valores_factu_prov)

