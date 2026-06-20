# -*- coding: utf-8 -*-
# from odoo import http


# class QuanLyKhachHang(http.Controller):
#     @http.route('/quan_ly_khach_hang/quan_ly_khach_hang', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/quan_ly_khach_hang/quan_ly_khach_hang/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('quan_ly_khach_hang.listing', {
#             'root': '/quan_ly_khach_hang/quan_ly_khach_hang',
#             'objects': http.request.env['quan_ly_khach_hang.quan_ly_khach_hang'].search([]),
#         })

#     @http.route('/quan_ly_khach_hang/quan_ly_khach_hang/objects/<model("quan_ly_khach_hang.quan_ly_khach_hang"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('quan_ly_khach_hang.object', {
#             'object': obj
#         })
