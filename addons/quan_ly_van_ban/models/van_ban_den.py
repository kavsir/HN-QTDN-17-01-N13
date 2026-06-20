from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class VanBanDen(models.Model):
    _name = 'van_ban_den'
    _description = 'Bảng chứa thông tin văn bản đến' 
    _rec_name = 'ten_van_ban' 

    # Các trường thông tin cơ bản sẵn có của bạn
    so_van_ban_den = fields.Char("Số đến", required=True)
    so_hieu_van_ban = fields.Char("Số/Ký hiệu gốc", required=True)
    ten_van_ban = fields.Char("Tên văn bản", required=True)
    noi_gui_den = fields.Char("Nơi gửi đến")

    # Các trường liên kết Many2one được bổ sung từ tài liệu hướng dẫn
    don_vi_nhan_id = fields.Many2one('don_vi', string="Đơn vị nhận xử lý") 
    nhan_vien_xu_ly_id = fields.Many2one('nhan_vien', string="Người xử lý chính") 
    loai_van_ban_id = fields.Many2one('loai_van_ban', string="Loại văn bản") 