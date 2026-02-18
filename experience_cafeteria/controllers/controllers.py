# from odoo import http


# class ExperienceCafeteria(http.Controller):
#     @http.route('/experience_cafeteria/experience_cafeteria', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/experience_cafeteria/experience_cafeteria/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('experience_cafeteria.listing', {
#             'root': '/experience_cafeteria/experience_cafeteria',
#             'objects': http.request.env['experience_cafeteria.experience_cafeteria'].search([]),
#         })

#     @http.route('/experience_cafeteria/experience_cafeteria/objects/<model("experience_cafeteria.experience_cafeteria"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('experience_cafeteria.object', {
#             'object': obj
#         })

