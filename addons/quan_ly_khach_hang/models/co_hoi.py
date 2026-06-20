from odoo import models, fields, api

class CoHoiKinhDoanh(models.Model):
    _name = 'crm.co.hoi'
    _description = 'Bảng chứa thông tin cơ hội khách hàng'
    _rec_name = 'ten_co_hoi'

    # 1. Nhóm Phân loại & Nguồn gốc
    ten_co_hoi = fields.Char("Tên cơ hội/Dự án", required=True)
    loai_khach_hang = fields.Selection([
        ('ca_nhan', 'Khách hàng cá nhân'),
        ('doanh_nghiep', 'Khách hàng doanh nghiệp')
    ], string="Loại khách hàng", default='doanh_nghiep')
    
    nguon_khach_hang = fields.Selection([
        ('website', 'Từ Website'),
        ('facebook', 'Từ Facebook / Zalo'),
        ('gioi_thieu', 'Được giới thiệu'),
        ('truc_tiep', 'Sale tự tìm kiếm')
    ], string="Nguồn khách hàng")

    # 2. Nhóm Thông tin liên hệ
    ten_doi_tac = fields.Char("Tên đối tác/Công ty")
    dien_thoai = fields.Char("Số điện thoại")
    email = fields.Char("Email khách hàng")

    # 3. Nhóm Chỉ số Kinh doanh (KPI)
    gia_tri_bao_gia = fields.Float("Giá trị dự kiến (VNĐ)")
    ngay_du_kien_chot = fields.Date("Ngày dự kiến chốt (Deadline)")
    
    muc_do_uu_tien = fields.Selection([
        ('0', 'Bình thường'),
        ('1', 'Thấp'),
        ('2', 'Cao'),
        ('3', 'Rất cao (VIP)')
    ], string="Độ ưu tiên", default='1')
    
    xac_suat_thanh_cong = fields.Integer("Xác suất chốt (%)", default=10)

    # 4. Nhóm Trạng thái & Phân quyền
    trang_thai = fields.Selection([
        ('moi', 'Mới tiếp nhận'),
        ('tiep_can', 'Đang tiếp cận'),
        ('bao_gia', 'Đang báo giá'),
        ('cho_duyet', 'Chờ duyệt báo giá'),
        ('thanh_cong', 'Thành công'),
        ('that_bai', 'Thất bại')
    ], string="Trạng thái", default='moi')

    nhan_vien_phu_trach_id = fields.Many2one('nhan_vien', string="Nhân viên phụ trách")

    # Logic 1: Tự động chuyển trạng thái khi giao việc
    @api.onchange('nhan_vien_phu_trach_id')
    def _onchange_nhan_vien_phu_trach(self):
        if self.nhan_vien_phu_trach_id and self.trang_thai == 'moi':
            self.trang_thai = 'tiep_can'

# Kế thừa ngược (Giữ nguyên để kết nối với module Công việc)
class KeThemCongViec(models.Model):
    _inherit = 'project.cong.viec'
    co_hoi_id = fields.Many2one('crm.co.hoi', string="Khách hàng", ondelete='cascade')