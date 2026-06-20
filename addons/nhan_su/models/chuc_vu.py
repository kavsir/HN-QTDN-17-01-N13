# Open file: addons/nhan_su/models/chuc_vu.py
from odoo import models, fields

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name = 'ten_chuc_vu'

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    
    # BỔ SUNG: Liên kết chức vụ trực tiếp vào Phòng ban (Đơn vị)
    don_vi_id = fields.Many2one('don_vi', string="Thuộc Phòng ban/Đơn vị", required=True, ondelete='cascade')