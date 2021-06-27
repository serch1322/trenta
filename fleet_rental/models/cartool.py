# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CarTools(models.Model):
    _name = 'car.tools'
    _description = 'Accesorios/Aditamentos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre" , required=True)
    num_eco = fields.Char(string="Número Económico", copy=False, readonly=True, index=True)
    num_serie = fields.Char(string="Número de Serie")
    costo = fields.Float(string="Costo")
    state = fields.Selection([('almacen','Almacén'),('disponible','Disponible'),('reservado','Reservado'),('renta','Renta'),('vendido','Vendido'),('servicio','Servicio')],
                             string="Estado",default='almacen',copy=False)
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user, index=True)

    marca = fields.Char(string="Marca")
    rent_price = fields.Float(string="Precio de Renta por Día")
    modelo = fields.Many2one('tools.category',string="Modelo")
    categoria = fields.Many2one('tools.categoria', string="Categoria")
    date_compra = fields.Date(string="Año de Compra")
    date_fabric = fields.Date(string="Año de Fabricacion")
    descripcion = fields.Char(string="Descripcion")
    tipo = fields.Selection([('aditamento', 'Aditamento'), ('accesorio', 'Accesorio')],
                            string="Tipo", copy=False, required=True)
    car = fields.Many2one('fleet.vehicle', string="Vehículo Asociado")

    @api.model
    def create(self, vals):
        vals['num_eco'] = self.env['ir.sequence'].next_by_code('secuencia.aditamentos')
        return super(CarTools, self).create(vals)

    def unlink(self):
        if self.id == True:
            raise UserError('No se puede eliminar ningun Accesorio o Aditamento registrado!')
        return super(CarTools, self).unlink()


    def vendido(self):
        self.state = 'vendido'

    def cambiar_disponible(self):
        self.state = 'disponible'


    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']

    def actividades(self):
        accesorios = self.env['car.tools'].search([])
        for accesorio in accesorios:
            if not accesorio.car.id:
                accesorio.activity_schedule('ligar_vehiculo_tools',user_id=accesorio.env['res.users'].id)
            else:
                return True








