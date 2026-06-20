from odoo import models, fields, api


class DonVi(models.Model):
    _name = 'don_vi'
    _description = 'Bảng chứa thông tin đơn vị'
    _rec_name = 'ten_don_vi'

    ma_don_vi = fields.Char("Mã đơn vị", required=True)
    ten_don_vi = fields.Char("Tên đơn vị", required=True)
    nhan_vien_ids = fields.One2many('nhan_vien', 'don_vi_id', string="Danh sách nhân viên")