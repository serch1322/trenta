# -*- coding: utf-8 -*-

import base64
import logging
from odoo import api, fields, models, tools, _
from odoo import modules
_logger = logging.getLogger(__name__)

class CarRentalChecklist(models.Model):
    _name = 'car.rental.checklist'

    name = fields.Char(string="Checklist")
    checklist_active = fields.Boolean(string="Disponible", default=True)
    checklist_number = fields.Many2one('car.rental.contract', string="Checklist Number")

class ChecklistRenta(models.Model):
    _inherit = 'car.rental.contract'

    # Cantidad Accesorios/Aditamentos
    cant_accesorio = fields.Integer(string="Cantidad de Accesorios", default=0)
    cant_aditamento = fields.Integer(string="Cantidad de Aditamentos", default=0)

    # Campos a Validar
    # Exterior Recepcion
    r_unidad_luces = fields.Boolean(string="Unidad de Luces", default=True, required=True)
    r_antena = fields.Boolean(string="Antena", default=True,required=True)
    r_espejo_izdo = fields.Boolean(string="Espejo Izquierdo", default=True, required=True)
    r_espejo_dcho = fields.Boolean(string="Espejo Derecho", default=True, required=True)
    r_cristales = fields.Boolean(string="Cristales", default=True, required=True)
    r_tapones_rines = fields.Boolean(string="Tapones Rines", default=True, required=True)
    r_limpiadores = fields.Boolean(string="Limpiadores", default=True, required=True)
    r_placa_d = fields.Boolean(string="Placa Delantera", default=True, required=True)
    r_placa_t = fields.Boolean(string="Placa Trasera", default=True, required=True)
    r_emblemas = fields.Boolean(string="Emblemas", default=True, required=True)

    # Interior Recepcion
    r_radio = fields.Boolean(string="Radio", default=True, required=True)
    r_encendedor = fields.Boolean(string="Encendedor", default=True, required=True)
    r_espejo_r = fields.Boolean(string="Espejo Retrovisor", default=True, required=True)
    r_tapete = fields.Boolean(string="Tapetes", default=True, required=True)
    r_alfombra = fields.Boolean(string="Alfombra", default=True, required=True)
    r_tarjeta_c = fields.Boolean(string="Tarjeta de Circulacion", default=True, required=True)
    r_poliza_s = fields.Boolean(string="Poliza de Seguro", default=True, required=True)

    # Exterior Entrega
    unidad_luces = fields.Boolean(string="Unidad de Luces", default=True,copy=False, required=True)
    antena = fields.Boolean(string="Antena", default=True,copy=False, required=True)
    espejo_izdo = fields.Boolean(string="Espejo Izquierdo", default=True,copy=False, required=True)
    espejo_dcho = fields.Boolean(string="Espejo Derecho", default=True,copy=False, required=True)
    cristales = fields.Boolean(string="Cristales", default=True,copy=False, required=True)
    tapones_rines = fields.Boolean(string="Tapones de Rines", default=True,copy=False, required=True)
    limpiadores = fields.Boolean(string="Limpiadores", default=True,copy=False, required=True)
    placa_d = fields.Boolean(string="Placa Delantera", default=True,copy=False, required=True)
    placa_t = fields.Boolean(string="Placa Trasera", default=True,copy=False, required=True)
    emblemas = fields.Boolean(string="Emblemas", default=True,copy=False, required=True)

    # Interior Entrega
    radio = fields.Boolean(string="Radio", default=True,copy=False, required=True)
    encendedor = fields.Boolean(string="Encendedor", default=True,copy=False, required=True)
    espejo_r = fields.Boolean(string="Espejo Retrovisor", default=True,copy=False, required=True)
    tapete = fields.Boolean(string="Tapetes", default=True,copy=False, required=True)
    alfombra = fields.Boolean(string="Alfombra", default=True,copy=False, required=True)
    tarjeta_c = fields.Boolean(string="Tarjeta de Circulacion", default=True,copy=False, required=True)
    poliza_s = fields.Boolean(string="Poliza de Seguro", default=True,copy=False, required=True)

    #Funciones para Jalar imagenes de static/img base64
    # superior
    def _get_default_image_superior(self):
        image_path = modules.get_module_resource('fleet_rental', 'static/img', 'arriba.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # Izquierdo
    def _get_default_image_izquierdo(self):
        image_path = modules.get_module_resource('fleet_rental', 'static/img', 'izquierda.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # Frente
    def _get_default_image_frente(self):
        image_path = modules.get_module_resource('fleet_rental', 'static/img', 'frente.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # Derecho
    def _get_default_image_derecho(self):
        image_path = modules.get_module_resource('fleet_rental', 'static/img', 'derecha.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # Trasero
    def _get_default_image_trasero(self):
        image_path = modules.get_module_resource('fleet_rental', 'static/img', 'atras.png')
        return base64.b64encode(open(image_path, 'rb').read())

    # imagenes Entrega vehiculo
    e_superior = fields.Binary(string="Superior", default=_get_default_image_superior)
    e_l_izquierdo = fields.Binary(string="Lateral Izquierdo", default=_get_default_image_izquierdo)
    e_frente = fields.Binary(string="Frente", default=_get_default_image_frente)
    e_l_derecho = fields.Binary(string="Lateral Derecho", default=_get_default_image_derecho)
    e_trasero = fields.Binary(string="Trasero", default=_get_default_image_trasero)
    comentario1 = fields.Text(string="nota")
    comentario2 = fields.Text(string="nota")
    comentario3 = fields.Text(string="nota")
    comentario4 = fields.Text(string="nota")
    comentario5 = fields.Text(string="nota")

    # Imagenes Recepcion vehiculo
    r_superior = fields.Binary(string="Superior", default=_get_default_image_superior)
    r_l_izquierdo = fields.Binary(string="Lateral Izquierdo", default=_get_default_image_izquierdo)
    r_frente = fields.Binary(string="Frente", default=_get_default_image_frente)
    r_l_derecho = fields.Binary(string="Lateral Derecho", default=_get_default_image_derecho)
    r_trasero = fields.Binary(string="Trasero", default=_get_default_image_trasero)
    comentario1r = fields.Text(string="nota")
    comentario2r = fields.Text(string="nota")
    comentario3r = fields.Text(string="nota")
    comentario4r = fields.Text(string="nota")
    comentario5r = fields.Text(string="nota")

    # Imagenes de Daños
    danos = fields.Boolean(string="hay daños?", default=False)
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
    firma_entrego_r = fields.Binary(string="Entregó:")
    firma_recibio_r = fields.Binary(string="Recibió:")
