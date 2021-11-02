# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import calendar


class CarRentalContract(models.Model):
    _name = 'car.rental.contract'
    _description = 'Fleet Rental Management'
    _inherit = 'mail.thread'

    @api.onchange('rent_start_date', 'rent_end_date')
    def check_availability(self):
        self.vehicle_id = ''
        fleet_obj = self.env['fleet.vehicle'].search([])
        for i in fleet_obj:
            # print("fleet_obj", i.read())
            for each in i.rental_reserved_time:
                if str(each.date_from) <= str(self.rent_start_date) <= str(each.date_to):
                    i.write({'rental_check_availability': False})
                elif str(self.rent_start_date) < str(each.date_from):
                    if str(each.date_from) <= str(self.rent_end_date) <= str(each.date_to):
                        i.write({'rental_check_availability': False})
                    elif str(self.rent_end_date) > str(each.date_to):
                        i.write({'rental_check_availability': False})
                    else:
                        i.write({'rental_check_availability': True})
                else:
                    i.write({'rental_check_availability': True})

    @api.depends('rent_concepts.subtotal','tools_line.subtotal')
    def _obtener_totales(self):
        for contract in self:
            total_concepts = 0.0
            total_tools = 0.0
            for line in contract.rent_concepts:
                total_concepts = total_concepts + line.subtotal
            for line in contract.tools_line:
                total_tools = total_tools + line.subtotal
            contract.total_concepts = total_concepts
            contract.total_tools = total_tools
            contract.grand_total = total_concepts + total_tools

    @api.onchange('tools_line')
    def cant_accesorios_aditamentos(self):
        self.cant_accesorio = 0
        self.cant_aditamento = 0
        x = 0
        y = 0
        for record in self.tools_line:
            if record.name.tipo == 'accesorio':
                x = x + 1
            else:
                y = y + 1
        self.cant_aditamento = y
        self.cant_accesorio = x

    # Cantidad Accesorios/Aditamentos
    cant_accesorio = fields.Integer(string="Cantidad de Accesorios", default=0)
    cant_aditamento = fields.Integer(string="Cantidad de Aditamentos", default=0)

    # Campos a Validar
    # Exterior Recepcion
    r_unidad_luces = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Unidad de Luces", default='bien',
                                      copy=False)
    r_antena = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Antena", default='bien', copy=False)
    r_espejo_izdo = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Izquierdo", default='bien')
    r_espejo_dcho = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Derecho", default='bien',
                                     copy=False)
    r_cristales = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Cristales", default='bien', copy=False)
    r_tapones_rines = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tapones Rines", default='bien',
                                       copy=False)
    r_limpiadores = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Limpiadores", default='bien', copy=False)
    r_placa_d = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Placa Delantera", default='bien', copy=False)
    r_placa_t = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Placa Trasera", default='bien', copy=False)

    # Interior Recepcion
    r_radio = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Radio", default='bien', copy=False)
    r_encendedor = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Encendedor", default='bien', copy=False)
    r_espejo_r = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Retrovisor", default='bien',
                                  copy=False)
    r_tapete = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tapete", default='bien', copy=False)
    r_alfombra = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Alfombra", default='bien', copy=False)
    r_tarjeta_c = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tarjeta de Circulacion", default='bien',
                                   copy=False)
    r_poliza_s = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Poliza de Seguro", default='bien',
                                  copy=False)

    # Exterior Entrega
    unidad_luces = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Unidad de Luces", default='bien',
                                    copy=False)
    antena = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Antena", default='bien', copy=False)
    espejo_izdo = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Izquierdo", default='bien')
    espejo_dcho = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Derecho", default='bien',
                                   copy=False)
    cristales = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Cristales", default='bien', copy=False)
    tapones_rines = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tapones Rines", default='bien',
                                     copy=False)
    limpiadores = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Limpiadores", default='bien', copy=False)
    placa_d = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Placa Delantera", default='bien', copy=False)
    placa_t = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Placa Trasera", default='bien', copy=False)

    # Interior Entrega
    radio = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Radio", default='bien', copy=False)
    encendedor = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Encendedor", default='bien', copy=False)
    espejo_r = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Espejo Retrovisor", default='bien',
                                copy=False)
    tapete = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tapete", default='bien', copy=False)
    alfombra = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Alfombra", default='bien', copy=False)
    tarjeta_c = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Tarjeta de Circulacion", default='bien',
                                 copy=False)
    poliza_s = fields.Selection([('bien', 'Bien'), ('mal', 'Mal')], string="Poliza de Seguro", default='bien', copy=False)

    # imagenes Entrega vehiculo
    e_superior = fields.Binary(string="Superior")
    e_l_izquierdo = fields.Binary(string="Lateral Izquierdo")
    e_frente = fields.Binary(string="Frente")
    e_l_derecho = fields.Binary(string="Lateral Derecho")
    e_trasero = fields.Binary(string="Trasero")
    comentario1 = fields.Text(string="nota")
    comentario2 = fields.Text(string="nota")
    comentario3 = fields.Text(string="nota")
    comentario4 = fields.Text(string="nota")
    comentario5 = fields.Text(string="nota")

    # Imagenes Recepcion vehiculo
    r_superior = fields.Binary(string="Superior")
    r_l_izquierdo = fields.Binary(string="Lateral Izquierdo")
    r_frente = fields.Binary(string="Frente")
    r_l_derecho = fields.Binary(string="Lateral Derecho")
    r_trasero = fields.Binary(string="Trasero")
    comentario1r = fields.Text(string="nota")
    comentario2r = fields.Text(string="nota")
    comentario3r = fields.Text(string="nota")
    comentario4r = fields.Text(string="nota")
    comentario5r = fields.Text(string="nota")

    # Imagenes de Daños
    imgd1 = fields.Binary(string="Daño 1")
    imgd2 = fields.Binary(string="Daño 2")
    imgd3 = fields.Binary(string="Daño 3")
    comentariod1 = fields.Text(string="nota")
    comentariod2 = fields.Text(string="nota")
    comentariod3 = fields.Text(string="nota")

    # Imagenes Entrega Aditamento
    adit_1 = fields.Binary(string="Aditamento 1")
    adit_2 = fields.Binary(string="Aditamento 2")
    adit_3 = fields.Binary(string="Aditamento 3")
    aditcom1 = fields.Text(string="nota")
    aditcom2 = fields.Text(string="nota")
    aditcom3 = fields.Text(string="nota")

    # Imagenes Recepcion Aditamento
    adit_1_r = fields.Binary(string="Aditamento 1")
    adit_2_r = fields.Binary(string="Aditamento 2")
    adit_3_r = fields.Binary(string="Aditamento 3")
    aditcom1_r = fields.Text(string="nota")
    aditcom2_r = fields.Text(string="nota")
    aditcom3_r = fields.Text(string="nota")

    # Imagenes Entrega Accesorio
    acces_1 = fields.Binary(string="Accesorio 1")
    acces_2 = fields.Binary(string="Accesorio 2")
    acces_3 = fields.Binary(string="Accesorio 3")
    acces_4 = fields.Binary(string="Accesorio 4")
    acces_5 = fields.Binary(string="Accesorio 5")
    acces_6 = fields.Binary(string="Accesorio 6")
    accescom1 = fields.Text(string="nota")
    accescom2 = fields.Text(string="nota")
    accescom3 = fields.Text(string="nota")
    accescom4 = fields.Text(string="nota")
    accescom5 = fields.Text(string="nota")
    accescom6 = fields.Text(string="nota")

    # Imagenes Recepcion Accesorio
    acces_1_r = fields.Binary(string="Accesorio 1")
    acces_2_r = fields.Binary(string="Accesorio 2")
    acces_3_r = fields.Binary(string="Accesorio 3")
    acces_4_r = fields.Binary(string="Accesorio 4")
    acces_5_r = fields.Binary(string="Accesorio 5")
    acces_6_r = fields.Binary(string="Accesorio 6")
    accescom1_r = fields.Text(string="nota")
    accescom2_r = fields.Text(string="nota")
    accescom3_r = fields.Text(string="nota")
    accescom4_r = fields.Text(string="nota")
    accescom5_r = fields.Text(string="nota")
    accescom6_r = fields.Text(string="nota")

    # Firmas
    firma_entrego = fields.Binary(string="Entregó:")
    firma_recibio = fields.Binary(string="Recibió:")


    grand_total = fields.Float(string="Total",readonly=True, store=True)
    image = fields.Binary(related='vehicle_id.image_128', string="Image of Vehicle")
    reserved_fleet_id = fields.Many2one('rental.fleet.reserved', invisible=True, copy=False)
    name = fields.Char(string="Name", default="Draft Contract", readonly=True, copy=False)
    customer_id = fields.Many2one('res.partner', required=True, string='Cliente', help="Customer")
    # vehicle_id = fields.Many2one('fleet.vehicle', string="Vehiculo", required=True, help="Vehicle", copy=False,
    #                              readonly=True,
    #                              states={'draft': [('readonly', False)]}
    #                              )
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehiculo", required=True, help="Vehicle", copy=False,
                                 readonly=True, states={'draft': [('readonly', False)]}, options="{'no_create': True}",
                                 domain="[('state_id.name', '=', 'Disponible'),('insurance_count','!=',0)]"
                                 )
    car_brand = fields.Many2one('fleet.vehicle.model.brand', string="Marca Vehiculo", size=50,
                                related='vehicle_id.model_id.brand_id', store=True, readonly=True)
    car_color = fields.Char(string="Color Vehiculo", size=50, related='vehicle_id.color', store=True, copy=False,
                            default='#FFFFFF', readonly=True)
    rent_start_date = fields.Date(string="Fecha Inicio de Renta", required=True, default=str(date.today()),
                                  help="Start date of contract", track_visibility='onchange', store=True, readonly=True, states={'draft': [('readonly', False)]})
    rent_end_date = fields.Date(string="Fecha Fin de Renta", help="End date of contract",
                                track_visibility='onchange', store=True)
    state = fields.Selection(
        [('draft', 'Borrador'), ('reserved', 'Reservado'), ('running', 'En Renta'), ('cancel', 'Cancelar'), ('service','Servicio'),
         ('checking', 'En Revisión'), ('invoice', 'Factura'), ('done', 'Finalizado')], string="State",
        default="draft", copy=False, track_visibility='onchange')
    notes = fields.Text(string="Notas")
    cost_frequency = fields.Selection([('monthly', 'Mensual')],
                                      string="Intervalo de Factura",
                                      help='Frecuencia de Generación de Factura', required=True)
    journal_type = fields.Many2one('account.journal', 'Journal',
                                   default=lambda self: self.env['account.journal'].search([('id', '=', 1)]))
    account_type = fields.Many2one('account.account', 'Account',
                                   default=lambda self: self.env['account.account'].search([('id', '=', 17)]))
    rent_concepts = fields.One2many('rent.concepts.line','sale_order_id',copy=True, readonly=True,states={'draft': [('readonly',False)] })
    total_concepts = fields.Float(string="Total (Conceptos)", compute="_obtener_totales", store=True)
    total_tools = fields.Float(string="Total (Accesorios/Aditamentos)", compute="_obtener_totales", store=True)
    first_payment = fields.Float(string='Anticipo',
                                 help="Transaction/Office/Contract charge amount, must paid by customer side other "
                                      "than recurrent payments",
                                 track_visibility='onchange',
                                 required=True)
    first_payment_inv = fields.Many2one('account.move', copy=False)
    first_invoice_created = fields.Boolean(string="First Invoice Created", invisible=True, copy=False)
    checklist_line = fields.One2many('car.rental.checklist', 'checklist_number', string="Checklist", ondelete='cascade',
                                     help="Facilities/Accessories, That should verify when closing the contract.",
                                     states={'invoice': [('readonly', True)],
                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]})
    tools_line = fields.One2many('car.rental.tools', 'accesorios', string="Accesorios/Aditamentos", ondelete='cascade', readonly=True,
                                     states={'draft': [('readonly',False)] })
    tools_missing_cost = fields.Float(string="Costo Perdido", readonly=True, copy=False,
                                      help='This is the total amount of missing tools/accessories')
    damage_cost = fields.Float(string="Costo de Daños", copy=False)
    damage_cost_sub = fields.Float(string="Costo de Daños", readonly=True, copy=False)
    total_cost = fields.Float(string="Total", readonly=True, copy=False)
    invoice_count = fields.Integer(compute='_invoice_count', string='# Factura', copy=False)
    check_verify = fields.Boolean(compute='check_action_verify', copy=False)
    sales_person = fields.Many2one('res.users', string='Encargado de Ventas', default=lambda self: self.env.uid,
                                   track_visibility='always')
    deposito = fields.Float(string="Deposito en Garantia", required=True, states={'draft': [('readonly',False)] })
    approved_driver = fields.Many2many('res.partner', string="Conductores Aprobados", tracking=True, copy=False,
                                     domain="[('company_id', '=', False)]")
    siguiente_fecha_de_factura = fields.Date(string="Fecha de Próxima Factura")
    sucursal = fields.Many2one('res.partner',string="Centro de Negocio", copy=False)

    @api.onchange('vehicle_id')
    def modificar_accesorios(self):
        for record in self:
            record.write({'tools_line':[(5,0,0)]})
            accesorios = self.env['car.tools'].search([('car', '=', record.vehicle_id.id)])
            lista_accesorios={}
            lista_valores = []
            for accesorio in accesorios:
                valores = {
                    'name': accesorio.id,
                    'num_eco': accesorio.num_eco,
                    'price': accesorio.rent_price
                }
                lista_valores.append((0,0,valores))
            lista_accesorios.update({
                'tools_line': lista_valores,
            })
        valores_accesorios = record.update(lista_accesorios)

    def crear_factura(self):
        self.ensure_one()
        inv_obj = self.env['account.move']
        today = date.today()
        valores_fact = {}
        accesorio = self.env['product.product'].search([("name", "=", "Accesorio/Aditamento")])
        if not self.siguiente_fecha_de_factura:
            start_date = self.rent_start_date
        else:
            start_date = self.siguiente_fecha_de_factura
        start_date_day = start_date.day
        next_month = datetime(start_date.year, start_date.month + 1, 1)
        end_date_month = datetime(start_date.year, start_date.month, calendar.mdays[start_date.month])
        end_date_day = end_date_month.day
        if self.state == 'running':
            self.siguiente_fecha_de_factura = next_month
            if self.cost_frequency == 'monthly':
                dias_a_facturar = end_date_day - start_date_day + 1
                valores_fact.update({
                    'partner_id': self.customer_id.id,
                    'invoice_payment_term_id': self.customer_id.property_payment_term_id.id,
                    'invoice_date': today,
                    'move_type': 'out_invoice',
                    'renta': self.id,
                    'inicio': start_date,
                    'fin': end_date_month,
                    'journal_id': 1,
                    'sucursal': self.sucursal.id,
                    'invoice_user_id': self.sales_person.id,
                })
                lista_factu = []
                if self.rent_concepts:
                    for linea in self.rent_concepts:
                        lineas_conceptos = {
                            'product_id': linea.name,
                            'name': linea.description,
                            'quantity': '%s' % (dias_a_facturar),
                            'price_unit': linea.price,
                            'tax_ids': linea.name.taxes_id,
                            'product_uom_id': linea.name.uom_id.id,
                            'vehiculo': self.vehicle_id.id,
                        }
                        lista_factu.append((0, 0, lineas_conceptos))
                if self.tools_line:
                    for linea in self.tools_line:
                        if linea.price != 0:
                            lineas_accesorios = {
                                'product_id': accesorio,
                                'name': linea.name.name,
                                'quantity': '%s' % (dias_a_facturar),
                                'price_unit': linea.price,
                                'tax_ids': accesorio.taxes_id,
                                'product_uom_id': accesorio.uom_id.id,
                                'aditamento': linea.name.id,
                            }
                            lista_factu.append((0, 0, lineas_accesorios))
                if lista_factu:
                    valores_fact.update({
                        'invoice_line_ids': lista_factu,
                    })
                factura_creada = inv_obj.create(valores_fact)

    @api.model
    def fleet_scheduler(self):
        inv_obj = self.env['account.move']
        today = date.today()
        valores_fact = {}
        accesorio = self.env['product.product'].search([("name", "=", "Accesorio/Aditamento")])
        for record in self.search([]):
            if not record.siguiente_fecha_de_factura:
                start_date = record.rent_start_date
            else:
                start_date = record.siguiente_fecha_de_factura
            start_date_day = start_date.day
            next_month = datetime(start_date.year, start_date.month + 1, 1)
            end_date_month = datetime(start_date.year, start_date.month, calendar.mdays[start_date.month])
            end_date_day = end_date_month.day
            if today < start_date:
                None
            else:
                if record.state == 'running':
                    record.siguiente_fecha_de_factura = next_month
                    if record.cost_frequency == 'monthly':
                        dias_a_facturar = end_date_day - start_date_day + 1
                        valores_fact.update({
                            'partner_id': record.customer_id.id,
                            'invoice_payment_term_id': record.customer_id.property_payment_term_id.id,
                            'invoice_date': today,
                            'move_type': 'out_invoice',
                            'renta': record.id,
                            'inicio': start_date,
                            'fin': end_date_month,
                            'journal_id': 1,
                            'sucursal': record.sucursal.id,
                            'invoice_user_id': record.sales_person.id,
                        })
                        lista_factu = []
                        if record.rent_concepts:
                            for linea in record.rent_concepts:
                                lineas_conceptos = {
                                    'product_id': linea.name,
                                    'name': linea.description,
                                    'quantity': '%s' % (dias_a_facturar),
                                    'price_unit': linea.price,
                                    'tax_ids': linea.name.taxes_id,
                                    'product_uom_id': linea.name.uom_id.id,
                                    'vehiculo': record.vehicle_id.id,
                                }
                                lista_factu.append((0, 0, lineas_conceptos))
                        if record.tools_line:
                            for linea in record.tools_line:
                                if linea.price != 0:
                                    lineas_accesorios = {
                                        'product_id': accesorio,
                                        'name': linea.name.name,
                                        'quantity': '%s' % (dias_a_facturar),
                                        'price_unit': linea.price,
                                        'tax_ids': accesorio.taxes_id,
                                        'product_uom_id': accesorio.uom_id.id,
                                        'aditamento': linea.name.id,
                                    }
                                    lista_factu.append((0, 0, lineas_accesorios))
                        if lista_factu:
                            valores_fact.update({
                                'invoice_line_ids': lista_factu,
                            })
                        factura_creada = inv_obj.create(valores_fact)


    def action_view_invoice(self):
        inv_obj = self.env['account.move'].search([('renta', '=', self.id)])
        inv_ids = []
        for each in inv_obj:
            inv_ids.append(each.id)
        view_id = self.env.ref('account.view_move_form').id
        if inv_ids:
            if len(inv_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids and inv_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', inv_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': inv_ids
                }

            return value

    def action_run(self):
        self.state = 'running'

    def revision(self):
        self.state = 'checking'

    def service(self):
        self.state = 'service'
        self.ensure_one()
        servicio = self.env['fleet.vehicle.log.services']
        valores_servicio = {}
        valores_servicio.update({
            'vehicle_id': self.vehicle_id.id,
            'service_type_id': 1,
        })
        servicio_creado = servicio.create(valores_servicio)


    def draft(self):
        self.state = 'draft'

    @api.depends('checklist_line.checklist_active')
    def check_action_verify(self):
        flag = 0
        for each in self:
            for i in each.checklist_line:
                if i.checklist_active:
                    continue
                else:
                    flag = 1
            if flag == 1:
                each.check_verify = False
            else:
                each.check_verify = True

    @api.constrains('rent_start_date', 'rent_end_date')
    def validate_dates(self):
        if self.cost_frequency == 'no':
            if self.rent_end_date < self.rent_start_date:
                raise Warning("Seleccionar Fecha Final Valida.")
        else:
            None

    def set_to_done(self):
        self.state = 'done'
        

    def _invoice_count(self):
        invoice_ids = self.env['account.move'].search([('renta', '=', self.id)])
        self.invoice_count = len(invoice_ids)

    @api.constrains('state')
    def state_changer(self):
        if self.state == "running":
            state_id = self.env.ref('fleet_rental.vehicle_state_rent').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "cancel":
            state_id = self.env.ref('fleet_rental.vehicle_state_active').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "invoice":
            self.rent_end_date = fields.Date.today()
            state_id = self.env.ref('fleet_rental.vehicle_state_rent').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "reserved":
            state_id = self.env.ref('fleet_rental.vehicle_state_inactive').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "done":
            state_id = self.env.ref('fleet_rental.vehicle_state_active').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "service":
            state_id = self.env.ref('fleet_rental.vehicle_state_inshop').id
            self.vehicle_id.write({'state_id': state_id})
        elif self.state == "checking":
            state_id = self.env.ref('fleet_rental.vehicle_state_recollection').id
            self.vehicle_id.write({'state_id': state_id})


    def fleet_scheduler1(self, rent_date):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        recurring_obj = self.env['fleet.rental.line']
        start_date = datetime.strptime(self.rent_start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(self.rent_end_date, '%Y-%m-%d').date()
        supplier = self.customer_id
        inv_data = {
            'ref': supplier.name,
            # 'account_id': supplier.property_account_payable_id.id,
            'partner_id': supplier.id,
            # 'currency_id': self.account_type.company_id.currency_id.id,
            # 'journal_id': self.journal_type.id,
            'invoice_origin': self.name,
            # 'company_id': self.account_type.company_id.id,
            'invoice_date_due': self.rent_end_date,
        }
        inv_id = inv_obj.create(inv_data)
        product_id = self.env['product.product'].search([("name", "=", "Fleet Rental Service")])
        if product_id.property_account_income_id.id:
            income_account = product_id.property_account_income_id
        elif product_id.categ_id.property_account_income_categ_id.id:
            income_account = product_id.categ_id.property_account_income_categ_id
        else:
            raise UserError(
                _('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                     product_id.id))
        recurring_data = {
            'name': self.vehicle_id.name,
            'date_today': rent_date,
            'account_info': income_account.name,
            'rental_number': self.id,
            'invoice_number': inv_id.id,
            'invoice_ref': inv_id.id,
        }
        recurring_obj.create(recurring_data)
        inv_line_data = {
            'name': self.vehicle_id.name,
            'account_id': income_account.id,
            'quantity': 1,
            'product_id': product_id.id,
            'move_id': inv_id.id,
        }
        inv_line_obj.update(inv_line_data)

    def action_verify(self):
        self.state = "invoice"
        self.reserved_fleet_id.unlink()
        self.rent_end_date = fields.Date.today()
        if self.total_cost != 0:
            inv_obj = self.env['account.move']
            inv_line_obj = self.env['account.move.line']
            supplier = self.customer_id
            inv_data = {
                # 'name': supplier.name,
                'ref': supplier.name,
                # 'account_id': supplier.property_account_payable_id.id,
                'partner_id': supplier.id,
                'currency_id': self.account_type.company_id.currency_id.id,
                'journal_id': self.journal_type.id,
                'invoice_origin': self.name,
                'company_id': self.account_type.company_id.id,
                'invoice_date_due': self.rent_end_date,
            }
            inv_id = inv_obj.create(inv_data)
            product_id = self.env['product.product'].search([("name", "=", "Fleet Rental Service")])
            if product_id.property_account_income_id.id:
                income_account = product_id.property_account_income_id
            elif product_id.categ_id.property_account_income_categ_id.id:
                income_account = product_id.categ_id.property_account_income_categ_id
            else:
                raise UserError(
                    _('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                         product_id.id))
            inv_line_data = {
                'name': "Damage/Tools missing cost",
                'account_id': income_account.id,
                'price_unit': self.total_cost,
                'quantity': 1,
                'product_id': product_id.id,
                'move_id': inv_id.id,
            }
            inv_line_obj.update(inv_line_data)
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.view_move_tree')
            list_view_id = self.env.ref('account.view_move_form', False)
            form_view_id = self.env.ref('account.view_move_tree', False)
            result = {
                'domain': "[('id', '=', " + str(inv_id) + ")]",
                'name': 'Fleet Rental Invoices',
                'view_mode': 'form',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'views': [(list_view_id.id, 'tree'), (form_view_id.id, 'form')],
            }
            # result = {
            #     # 'name': action.name,
            #     'help': action.help,
            #     'type': 'ir.actions.act_window',
            #     'views': [[list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'kanban'],
            #               [False, 'calendar'], [False, 'pivot']],
            #     'target': action.target,
            #     'context': action.context,
            #     'res_model': 'account.move',
            # }
            if len(inv_id) > 1:
                result['domain'] = "[('id','in',%s)]" % inv_id.ids
            elif len(inv_id) == 1:
                result['views'] = [(form_view_id, 'form')]
                result['res_id'] = inv_id.ids[0]
            else:
                result = {'type': 'ir.actions.act_window_close'}
            return result

    def action_confirm(self):
        check_availability = 0
        for each in self.vehicle_id.rental_reserved_time:
            if each.date_from <= self.rent_start_date <= each.date_to:
                check_availability = 1
            elif self.rent_start_date < each.date_from:
                if each.date_from <= self.rent_end_date <= each.date_to:
                    check_availability = 1
                elif self.rent_end_date > each.date_to:
                    check_availability = 1
                else:
                    check_availability = 0
            else:
                check_availability = 0
        if check_availability == 0:
            reserved_id = self.vehicle_id.rental_reserved_time.create({'customer_id': self.customer_id.id,
                                                                       'date_from': self.rent_start_date,
                                                                       'date_to': self.rent_end_date,
                                                                       'reserved_obj': self.vehicle_id.id
                                                                       })
            self.write({'reserved_fleet_id': reserved_id.id})
        else:
            raise Warning('Sorry This vehicle is already booked by another customer')
        self.state = "reserved"
        sequence_code = 'secuencia.renta.de.carro'
        order_date = self.create_date
        order_date = str(order_date)[0:10]
        self.name = self.env['ir.sequence'] \
            .with_context(ir_sequence_date=order_date).next_by_code(sequence_code)

    def action_cancel(self):
        self.state = "cancel"
        if self.reserved_fleet_id:
            self.reserved_fleet_id.unlink()

    def force_checking(self):
        self.state = "checking"

    def action_invoice_create(self):
        for each in self:
            rent_date = self.rent_start_date
            if each.cost_frequency != 'no' and rent_date < date.today():
                rental_days = (date.today() - rent_date).days
                if each.cost_frequency == 'weekly':
                    rental_days = int(rental_days / 7)
                if each.cost_frequency == 'monthly':
                    rental_days = int(rental_days / 30)
                for each1 in range(0, rental_days + 1):
                    if rent_date > datetime.strptime(each.rent_end_date, "%Y-%m-%d").date():
                        break
                    each.fleet_scheduler1(rent_date)
                    if each.cost_frequency == 'daily':
                        rent_date = rent_date + timedelta(days=1)
                    if each.cost_frequency == 'weekly':
                        rent_date = rent_date + timedelta(days=7)
                    if each.cost_frequency == 'monthly':
                        rent_date = rent_date + timedelta(days=30)

        if self.first_payment != 0:
            self.first_invoice_created = True
            inv_obj = self.env['account.move']
            inv_line_obj = self.env['account.move.line']
            supplier = self.customer_id
            inv_data = {
                # 'name': supplier.name,
                'ref': supplier.name,
                'move_type': 'out_invoice',
                # 'account_id': supplier.property_account_payable_id.id,
                'partner_id': supplier.id,
                'currency_id': self.account_type.company_id.currency_id.id,
                'journal_id': self.journal_type.id,
                'invoice_origin': self.name,
                'company_id': self.account_type.company_id.id,
                'invoice_date_due': self.rent_end_date,
            }
            inv_id = inv_obj.create(inv_data)
            print(inv_id, 'hi')
            self.first_payment_inv = inv_id.id
            product_id = self.env['product.product'].search([("name", "=", "Anticipo")])
            if product_id.property_account_income_id.id:
                income_account = product_id.property_account_income_id.id
            elif product_id.categ_id.property_account_income_categ_id.id:
                income_account = product_id.categ_id.property_account_income_categ_id.id
            else:
                raise UserError(
                    _('Please define income account for this product: "%s" (id:%d).') % (product_id.name,
                                                                                         product_id.id))

            if inv_id:
                list_value = [(0, 0, {
                    'name': self.vehicle_id.name,
                    'price_unit': self.first_payment,
                    'quantity': 1.0,
                    'account_id': income_account,
                    'product_id': product_id.id,
                    'move_id': inv_id.id,
                })]
                inv_id.write({'invoice_line_ids': list_value})
            imd = self.env['ir.model.data']
            action = imd.xmlid_to_object('account.action_move_out_invoice_type')
            result = {
                'name': action.name,
                'type': 'ir.actions.act_window',
                'views': [[False, 'form']],
                'target': 'current',
                'res_id': inv_id.id,
                'res_model': 'account.move',
            }
            return result

        else:
            raise Warning("Please enter advance amount to make first payment")

class RentConcepts(models.Model):
    _name = 'rent.concepts.line'

    @api.depends('qty', 'price')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price

    name = fields.Many2one('product.product', string="Producto", domain="[('sale_ok', '=', True)]")
    description = fields.Char(string="Descripción")
    price = fields.Float(string="Precio de Renta por Día")
    qty = fields.Float(string="Cantidad", default=1)
    subtotal = fields.Float(string="Subtotal", compute="_get_subtotal", store=True)
    sale_order_id = fields.Many2one('car.rental.contract',string="Orden de Renta")

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.price = self.name.lst_price

    @api.onchange('name')
    def _get_descripcion(self):
        for line in self:
            line.description = line.name.description_sale

class CarRentalChecklist(models.Model):
    _name = 'car.rental.tools'

    @api.depends('qty', 'price')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price

    name = fields.Many2one('car.tools', string="Accesorio")
    accesorios = fields.Many2one('car.rental.contract',string="Accesorios")
    num_eco = fields.Char(string="Número Económico")
    price = fields.Float(string="Precio de Renta por Día")
    qty = fields.Float(string="Cantidad", default=1)
    subtotal = fields.Float(string="Subtotal", compute="_get_subtotal", store=True)


