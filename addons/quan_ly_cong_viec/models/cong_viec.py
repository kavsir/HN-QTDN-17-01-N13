from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CongViecChamSoc(models.Model):
    _name = 'project.cong.viec'
    _description = 'Bảng chứa các đầu việc chăm sóc khách hàng'
    _rec_name = 'ten_cong_viec'

    # 1. Thông tin chung
    ten_cong_viec = fields.Char("Tên đầu việc", required=True)
    loai_cong_viec = fields.Selection([
        ('goi_dien', 'Gọi điện tư vấn'),
        ('gui_email', 'Gửi Email báo giá'),
        ('gap_mat', 'Hẹn gặp trực tiếp'),
        ('ky_hop_dong', 'Ký kết hợp đồng')
    ], string="Hình thức", default='goi_dien')

    # 2. Thời gian & Tiến độ
    ngay_bat_dau = fields.Date("Ngày bắt đầu", default=fields.Date.context_today)
    han_chot = fields.Date("Hạn chót (Deadline)")
    tien_do_phan_tram = fields.Integer("Tiến độ hoàn thành (%)", default=0)
    
    do_uu_tien = fields.Selection([
        ('0', 'Thấp'),
        ('1', 'Bình thường'),
        ('2', 'Cao'),
        ('3', 'Khẩn cấp')
    ], string="Mức độ khẩn cấp", default='1')

    # 3. Kết quả & Đánh giá
    ghi_chu = fields.Text("Nội dung / Kết quả thực hiện")
    
    trang_thai_cong_viec = fields.Selection([
        ('chua_lam', 'Chưa thực hiện'),
        ('dang_lam', 'Đang thực hiện'),
        ('hoan_thanh', 'Hoàn thành'),
        ('huy', 'Đã hủy')
    ], string="Trạng thái", default='chua_lam')

    # 4. Liên kết gốc (HRM)
    nhan_vien_thuc_hien_id = fields.Many2one('nhan_vien', string="Người thực hiện")

    # ==================== LOGIC TỰ ĐỘNG HÓA NÂNG CAO ====================

    @api.onchange('trang_thai_cong_viec')
    def _onchange_trang_thai_cong_viec(self):
        """ Thay đổi tiến độ tương ứng theo trạng thái """
        for record in self:
            if record.trang_thai_cong_viec == 'hoan_thanh':
                record.tien_do_phan_tram = 100
            elif record.trang_thai_cong_viec == 'chua_lam':
                record.tien_do_phan_tram = 0

    @api.onchange('tien_do_phan_tram')
    def _onchange_tien_do_phan_tram(self):
        """ Tự động nhảy trạng thái dựa trên % tiến độ nhập vào """
        for record in self:
            if record.tien_do_phan_tram >= 100:
                record.trang_thai_cong_viec = 'hoan_thanh'
            elif record.tien_do_phan_tram > 0 and record.trang_thai_cong_viec == 'chua_lam':
                record.trang_thai_cong_viec = 'dang_lam'
            elif record.tien_do_phan_tram == 0 and record.trang_thai_cong_viec == 'dang_lam':
                record.trang_thai_cong_viec = 'chua_lam'

    @api.constrains('tien_do_phan_tram')
    def _check_tien_do_phan_tram(self):
        """ Ngăn chặn nhập số % tiến độ phi lý """
        for record in self:
            if record.tien_do_phan_tram < 0 or record.tien_do_phan_tram > 100:
                raise ValidationError("Tiến độ hoàn thành công việc bắt buộc phải nằm trong khoảng từ 0% đến 100%!")