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
    # Chèn dòng này ngay bên dưới trường nhan_vien_phu_trach_id
    don_vi_id = fields.Many2one(
        'don_vi', 
        string="Phòng ban phụ trách", 
        related='nhan_vien_phu_trach_id.don_vi_id', 
        store=True
    )
    # 🛠️ BỔ SUNG: Mối quan hệ một-nhiều để hiển thị danh sách công việc liên quan
    project_cong_viec_ids = fields.One2many('project.cong.viec', 'co_hoi_id', string="Công việc liên quan")

    # 🛠️ BỔ SUNG: Tự động cập nhật xác suất thành công theo tiến trình cơ hội khách hàng
    @api.onchange('trang_thai')
    def _onchange_trang_thai(self):
        for record in self:
            if record.trang_thai == 'moi':
                record.xac_suat_thanh_cong = 10
            elif record.trang_thai == 'tiep_can':
                record.xac_suat_thanh_cong = 30
            elif record.trang_thai == 'bao_gia':
                record.xac_suat_thanh_cong = 50
            elif record.trang_thai == 'cho_duyet':
                record.xac_suat_thanh_cong = 80
            elif record.trang_thai == 'thanh_cong':
                record.xac_suat_thanh_cong = 100
            elif record.trang_thai == 'that_bai':
                record.xac_suat_thanh_cong = 0

    so_luong_cong_viec = fields.Integer(string="Số công việc", compute="_compute_so_luong_cong_viec")

    def _compute_so_luong_cong_viec(self):
        for record in self:

            record.so_luong_cong_viec = self.env['project.cong.viec'].search_count([('co_hoi_id', '=', record.id)])

    def action_view_cong_viec(self):
        self.ensure_one()
        return {
            'name': f'Công việc: {self.ten_co_hoi}',
            'type': 'ir.actions.act_window',
            'res_model': 'project.cong.viec',
            'view_mode': 'kanban,tree,form,graph,pivot',
            'domain': [('co_hoi_id', '=', self.id)], 
            'context': {'default_co_hoi_id': self.id}, 
        }
class KeThemCongViec(models.Model):
    _inherit = 'project.cong.viec'
    
    co_hoi_id = fields.Many2one('crm.co.hoi', string="Khách hàng", ondelete='cascade')