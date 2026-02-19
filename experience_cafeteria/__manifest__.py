{
    'name': 'Gestión de Experiencia del Cliente',
    'version': '1.0',
    'summary': 'Encuestas, quejas, sugerencias y preferencias de clientes para cafetería',
    'description': """
        Módulo para mejorar la experiencia del cliente en cafetería:
        - Encuestas de satisfacción post-servicio
        - Sistema de quejas y sugerencias rápido
        - Perfil de cliente con preferencias (café favorito, temperatura, etc.)
        - Alertas de clientes habituales al hacer pedido
        - Historial de visitas y gasto por cliente
        - Sistema de feedback con código QR en ticket
    """,
    'author': 'Carlos Torres, Ana Olmos - Cafetería La Esquina',
    'website': 'https://localhost:8069',
    'category': 'Sales/Point of Sale',
    'depends': ['point_of_sale', 'crm', 'hr'],
    'data': [
        'security/experience_groups.xml',
        'security/ir.model.access.csv',
        'data/experience_data.xml',
        'views/experience_views.xml',
        'views/experience_menus.xml',
        'views/experience_templates.xml',
        'reports/experience_reports.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': True,
}