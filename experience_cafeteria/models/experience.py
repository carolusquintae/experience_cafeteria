from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ClientePreferencias(models.Model):
    _name = 'cliente.preferencias'
    _description = 'Preferencias y hábitos del cliente'
    _rec_name = 'cliente_id'
    _order = 'fecha_ultima_visita desc'

    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True, ondelete='cascade')
    telefono = fields.Char(related='cliente_id.phone', string='Teléfono')
    email = fields.Char(related='cliente_id.email', string='Email')
    
    # Preferencias de bebida
    bebida_favorita = fields.Many2one(
        'product.product', string='Bebida favorita', 
        domain=[('categ_id.name', '=', 'Bebidas')]
    )

    tipo_cafe = fields.Selection([
        ('expresso', 'Expresso'),
        ('con_leche', 'Con leche'),
        ('cortado', 'Cortado'),
        ('capuchino', 'Capuchino'),
        ('americano', 'Americano'),
        ('descafeinado', 'Descafeinado')
    ], string='Tipo de café preferido')
    
    temperatura_preferida = fields.Selection([
        ('muy_caliente', 'Muy caliente'),
        ('normal', 'Normal'),
        ('templado', 'Templado'),
        ('frio', 'Frío')
    ], string='Temperatura preferida')
    
    tipo_leche = fields.Selection([
        ('entera', 'Leche entera'),
        ('semidesnatada', 'Semidesnatada'),
        ('desnatada', 'Desnatada'),
        ('soja', 'Leche de soja'),
        ('almendra', 'Leche de almendra'),
        ('avena', 'Leche de avena'),
        ('sin_lactosa', 'Sin lactosa')
    ], string='Tipo de leche')
    
    azucar = fields.Selection([
        ('sin', 'Sin azúcar'),
        ('poco', 'Poco'),
        ('normal', 'Normal'),
        ('mucho', 'Mucho'),
        ('edulcorante', 'Edulcorante')
    ], string='Azúcar/Edulcorante')
    
    # Preferencias de comida
    comida_favorita = fields.Many2one(
        'product.product', string='Plato favorito',
        domain=[('categ_id.name', '=', 'Comidas')]
    )

    alergenos = fields.Many2many('product.alergenos', string='Alérgenos')
    observaciones_dieta = fields.Text('Observaciones dietéticas')
    
    # Estadísticas
    visitas_totales = fields.Integer('Visitas totales', default=0, compute='_compute_estadisticas', store=True)
    gasto_total = fields.Float('Gasto total (€)', compute='_compute_estadisticas', store=True)
    gasto_medio_visita = fields.Float('Gasto medio por visita (€)', compute='_compute_estadisticas', store=True)
    fecha_primera_visita = fields.Date('Primera visita', compute='_compute_estadisticas', store=True)
    fecha_ultima_visita = fields.Date('Última visita', compute='_compute_estadisticas', store=True)
    cliente_habitual = fields.Boolean('Cliente habitual', compute='_compute_habitual', store=True)
    
    @api.depends('cliente_id.pos_order_ids')
    def _compute_estadisticas(self):
        for record in self:
            orders = record.cliente_id.pos_order_ids.filtered(lambda o: o.state == 'paid')
            record.visitas_totales = len(orders)
            record.gasto_total = sum(orders.mapped('amount_total'))
            record.gasto_medio_visita = record.gasto_total / record.visitas_totales if record.visitas_totales else 0
            if orders:
                fechas = orders.mapped('date_order')
                record.fecha_primera_visita = min(fechas).date() if fechas else False
                record.fecha_ultima_visita = max(fechas).date() if fechas else False
    
    @api.depends('visitas_totales')
    def _compute_habitual(self):
        for record in self:
            record.cliente_habitual = record.visitas_totales >= 5


class EncuestaSatisfaccion(models.Model):
    _name = 'encuesta.satisfaccion'
    _description = 'Encuestas de satisfacción de clientes'
    _order = 'fecha desc'

    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True)
    pedido_id = fields.Many2one('pos.order', string='Pedido asociado')
    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)
    
    # Puntuaciones (1-5)
    puntuacion_general = fields.Selection([
        ('1', '★☆☆☆☆ Muy malo'),
        ('2', '★★☆☆☆ Malo'),
        ('3', '★★★☆☆ Normal'),
        ('4', '★★★★☆ Bueno'),
        ('5', '★★★★★ Excelente')
    ], string='Puntuación general', required=True)
    
    puntuacion_comida = fields.Selection([
        ('1', '★☆☆☆☆'), ('2', '★★☆☆☆'), ('3', '★★★☆☆'), ('4', '★★★★☆'), ('5', '★★★★★')
    ], string='Comida')
    
    puntuacion_bebida = fields.Selection([
        ('1', '★☆☆☆☆'), ('2', '★★☆☆☆'), ('3', '★★★☆☆'), ('4', '★★★★☆'), ('5', '★★★★★')
    ], string='Bebida')
    
    puntuacion_servicio = fields.Selection([
        ('1', '★☆☆☆☆'), ('2', '★★☆☆☆'), ('3', '★★★☆☆'), ('4', '★★★★☆'), ('5', '★★★★★')
    ], string='Servicio')
    
    puntuacion_ambiente = fields.Selection([
        ('1', '★☆☆☆☆'), ('2', '★★☆☆☆'), ('3', '★★★☆☆'), ('4', '★★★★☆'), ('5', '★★★★★')
    ], string='Ambiente/Limpieza')
    
    # Preguntas adicionales
    volveria = fields.Boolean('¿Volvería?', default=True)
    recomendaria = fields.Boolean('¿Recomendaría?', default=True)
    comentario = fields.Text('Comentario/Sugerencia')
    
    # Campos calculados
    media_puntuacion = fields.Float('Puntuación media', compute='_compute_media', store=True)
    nivel_satisfaccion = fields.Selection([
        ('bajo', '🔴 Bajo'),
        ('medio', '🟡 Medio'),
        ('alto', '🟢 Alto')
    ], string='Nivel satisfacción', compute='_compute_nivel', store=True)
    
    @api.depends('puntuacion_general', 'puntuacion_comida', 'puntuacion_bebida', 'puntuacion_servicio', 'puntuacion_ambiente')
    def _compute_media(self):
        for record in self:
            puntuaciones = []
            if record.puntuacion_general:
                puntuaciones.append(int(record.puntuacion_general))
            if record.puntuacion_comida:
                puntuaciones.append(int(record.puntuacion_comida))
            if record.puntuacion_bebida:
                puntuaciones.append(int(record.puntuacion_bebida))
            if record.puntuacion_servicio:
                puntuaciones.append(int(record.puntuacion_servicio))
            if record.puntuacion_ambiente:
                puntuaciones.append(int(record.puntuacion_ambiente))
            
            if puntuaciones:
                record.media_puntuacion = sum(puntuaciones) / len(puntuaciones)
            else:
                record.media_puntuacion = 0
    
    @api.depends('media_puntuacion')
    def _compute_nivel(self):
        for record in self:
            if record.media_puntuacion < 3:
                record.nivel_satisfaccion = 'bajo'
            elif record.media_puntuacion < 4:
                record.nivel_satisfaccion = 'medio'
            else:
                record.nivel_satisfaccion = 'alto'
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for res in records:
            # Si la puntuación es baja, crear automáticamente una queja/incidencia
            if res.nivel_satisfaccion == 'bajo':
                self.env['queja.sugerencia'].create({
                    'cliente_id': res.cliente_id.id,
                    'encuesta_id': res.id,
                    'tipo': 'queja',
                    'categoria': 'otro',
                    'descripcion': res.comentario or 'Cliente insatisfecho (sin comentario)',
                    'prioridad': 'alta',
                    'estado': 'pendiente'
                })
        return records


class QuejaSugerencia(models.Model):
    _name = 'queja.sugerencia'
    _description = 'Quejas y sugerencias de clientes'
    _rec_name = 'descripcion'
    _order = 'fecha desc, prioridad desc'

    cliente_id = fields.Many2one('res.partner', string='Cliente')
    encuesta_id = fields.Many2one('encuesta.satisfaccion', string='Encuesta relacionada')
    fecha = fields.Datetime('Fecha', default=fields.Datetime.now)
    
    tipo = fields.Selection([
        ('queja', 'Queja'),
        ('sugerencia', 'Sugerencia'),
        ('reclamo', 'Reclamo'),
        ('felicitacion', 'Felicitación')
    ], string='Tipo', required=True)
    
    prioridad = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ], string='Prioridad', default='media')
    
    categoria = fields.Selection([
        ('servicio', 'Servicio'),
        ('comida', 'Comida'),
        ('bebida', 'Bebida'),
        ('limpieza', 'Limpieza'),
        ('precio', 'Precio'),
        ('espera', 'Tiempo de espera'),
        ('instalaciones', 'Instalaciones'),
        ('otro', 'Otro')
    ], string='Categoría', required=True)
    
    descripcion = fields.Text('Descripción', required=True)
    accion_tomada = fields.Text('Acción tomada')
    
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado')
    ], string='Estado', default='pendiente')
    
    responsable_id = fields.Many2one('hr.employee', string='Responsable')
    fecha_resolucion = fields.Datetime('Fecha de resolución')
    
    # Campos para seguimiento
    notificar_cliente = fields.Boolean('Notificar al cliente', default=True)
    notificado = fields.Boolean('Notificado')
    
    def action_resolver(self):
        self.estado = 'resuelto'
        self.fecha_resolucion = fields.Datetime.now()


class SeguimientoCliente(models.Model):
    _name = 'seguimiento.cliente'
    _description = 'Seguimiento de acciones con clientes'
    _order = 'fecha desc'

    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True)
    fecha = fields.Datetime('Fecha', default=fields.Datetime.now)
    tipo_accion = fields.Selection([
        ('llamada', 'Llamada'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('presencial', 'Presencial'),
        ('regalo', 'Regalo/Compensación'),
        ('otro', 'Otro')
    ], string='Tipo de acción', required=True)
    
    descripcion = fields.Text('Descripción', required=True)
    empleado_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    
    # Campos relacionados con quejas/encuestas
    queja_id = fields.Many2one('queja.sugerencia', string='Queja relacionada')
    encuesta_id = fields.Many2one('encuesta.satisfaccion', string='Encuesta relacionada')
    
    resultado = fields.Text('Resultado/Feedback')


class ProductAlergenos(models.Model):
    _name = 'product.alergenos'
    _description = 'Alérgenos alimentarios'

    name = fields.Char('Nombre del alérgeno', required=True)
    codigo = fields.Char('Código', required=True)
    descripcion = fields.Text('Descripción')
    icono = fields.Binary('Icono')
    
    producto_ids = fields.Many2many('product.product', string='Productos que lo contienen')