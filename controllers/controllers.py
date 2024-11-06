# -*- coding: utf-8 -*-
# from odoo import http


# class SchoolManagementSystem(http.Controller):
#     @http.route('/school_management_system/school_management_system', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/school_management_system/school_management_system/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('school_management_system.listing', {
#             'root': '/school_management_system/school_management_system',
#             'objects': http.request.env['school_management_system.school_management_system'].search([]),
#         })

#     @http.route('/school_management_system/school_management_system/objects/<model("school_management_system.school_management_system"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school_management_system.object', {
#             'object': obj
#         })

