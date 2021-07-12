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


    grand_total = fields.Float(string="Total",readonly=True, store=True)
    image = fields.Binary(related='vehicle_id.image_128', string="Image of Vehicle")
    reserved_fleet_id = fields.Many2one('rental.fleet.reserved', invisible=True, copy=False)
    name = fields.Char(string="Name", default="Draft Contract", readonly=True, copy=False)
    customer_id = fields.Many2one('res.partner', required=True, string='Cliente', help="Customer")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehiculo", required=True, help="Vehicle", copy=False,
                                 readonly=True,
                                 states={'draft': [('readonly', False)]}
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
        [('draft', 'Borrador'), ('reserved', 'Reservado'), ('running', 'Corriendo'), ('cancel', 'Cancelar'), ('service','Servicio'),
         ('checking', 'Revisando'), ('invoice', 'Factura'), ('done', 'Hecho')], string="State",
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

    def fleet_scheduler(self):
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
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        print("self.name", self.name)
        f = 0
        for each in invoice_ids:
            if each.payment_state != 'paid':
                f = 1
                break
        if f == 0:
            self.state = 'done'
        else:
            raise UserError("Some Invoices are pending")

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


