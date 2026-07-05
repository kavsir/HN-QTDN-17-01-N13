from odoo import models, fields, api
from datetime import timedelta

# =========================================================================
# 1. LỚP ĐƯỢC THÊM MỚI: BẢNG DANH MỤC MẪU CÔNG VIỆC CHUẨN (TASK TEMPLATE)
# =========================================================================
class CongViecMau(models.Model):
    _name = 'cong_viec_mau'
    _description = 'Checklist mẫu khi chốt hợp đồng'
    
    name = fields.Char("Tên đầu việc mẫu", required=True)
    loai_cong_viec = fields.Selection([
        ('khao_sat', 'Khảo sát / Đánh giá'),
        ('trien_khai', 'Triển khai kỹ thuật'),
        ('dao_tao', 'Đào tạo / Bàn giao'),
        ('ho_so', 'Xử lý hồ sơ / Kế toán')
    ], string="Loại công việc")
    don_vi_thuc_hien_id = fields.Many2one('don_vi', string="Phòng ban phụ trách", required=True)
    so_ngay_hoan_thanh = fields.Integer("Số ngày chuẩn (SLA)", default=1, help="Số ngày để hoàn thành tính từ lúc chốt hợp đồng")


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

    nhan_vien_phu_trach_id = fields.Many2one(
        'nhan_vien', 
        string="Nhân viên phụ trách",
        domain="[('trang_thai_lam_viec', '=', 'dang_lam'), ('don_vi_id.ten_don_vi', 'ilike', 'Kinh Doanh')]"
    )
    
    don_vi_id = fields.Many2one(
        'don_vi', 
        string="Phòng ban phụ trách", 
        related='nhan_vien_phu_trach_id.don_vi_id', 
        store=True
    )

    project_cong_viec_ids = fields.One2many('project.cong.viec', 'co_hoi_id', string="Công việc liên quan")

    # GHI CHÚ (Fix Rủi ro #3 - Trigger sinh task sai điều kiện / spam):
    # Cờ đánh dấu checklist đã được tự động sinh ra hay chưa. Trước đây write()
    # chỉ kiểm tra vals.get('trang_thai') == 'thanh_cong' mà KHÔNG kiểm tra
    # trạng thái trước đó -> mỗi lần người dùng bấm Lưu (Save) trên form khi
    # trạng thái đang là 'thanh_cong' (dù không đổi gì), hệ thống vẫn sinh
    # thêm một loạt task mới -> loãng danh sách Quản lý công việc, spam thông báo.
    da_sinh_checklist_tu_dong = fields.Boolean(
        "Đã sinh checklist tự động", default=False, copy=False,
        help="Đánh dấu để đảm bảo checklist công việc chỉ được hệ thống tự sinh"
             " đúng MỘT LẦN khi cơ hội chuyển sang Thành công, tránh sinh lặp/spam."
    )

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

    # =========================================================================
    # LOGIC AUTOMATION ĐƯỢC CHÈN VÀO ĐÂY (NẰM TRONG CLASS COHOIKINHDOANH)
    # =========================================================================
    def write(self, vals):
        # FIX Rủi ro #3: xác định TRƯỚC khi ghi, những bản ghi nào thực sự đang
        # CHUYỂN TRẠNG THÁI sang 'thanh_cong' (không phải đã ở sẵn trạng thái này)
        # và CHƯA từng được sinh checklist tự động. Chỉ nhóm bản ghi này mới được
        # phép sinh task - đảm bảo Trigger chỉ chạy đúng 1 lần / cơ hội, không phụ
        # thuộc vào việc người dùng bấm Lưu bao nhiêu lần.
        can_sinh_checklist = self.env['crm.co.hoi']
        if vals.get('trang_thai') == 'thanh_cong':
            can_sinh_checklist = self.filtered(
                lambda r: r.trang_thai != 'thanh_cong' and not r.da_sinh_checklist_tu_dong
            )

        # Thực hiện cập nhật trạng thái của cơ hội khách hàng trước
        res = super(CoHoiKinhDoanh, self).write(vals)

        if can_sinh_checklist:
            for record in can_sinh_checklist:
                record._sinh_checklist_cong_viec_tu_dong()
            # Đánh dấu đã sinh - chặn mọi lần Lưu tiếp theo không sinh lại nữa
            can_sinh_checklist.write({'da_sinh_checklist_tu_dong': True})

        return res

    def _sinh_checklist_cong_viec_tu_dong(self):
        """ Quét bảng danh mục mẫu để tự động hóa sinh việc giao cho các phòng ban """
        danh_sach_mau = self.env['cong_viec_mau'].search([])
        CongViec = self.env['project.cong.viec']
        
        for mau in danh_sach_mau:
            # Tìm kiếm Trưởng phòng của đơn vị chịu trách nhiệm thực hiện công việc mẫu
            truong_phong = self.env['nhan_vien'].search([
                ('don_vi_id', '=', mau.don_vi_thuc_hien_id.id),
                ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Trưởng'),
                ('trang_thai_lam_viec', '=', 'dang_lam')
            ], limit=1)
            
            # Tính toán hạn chót xử lý dựa trên cấu hình SLA (Số ngày hoàn thành)
            han_chot = fields.Date.context_today(self) + timedelta(days=mau.so_ngay_hoan_thanh)
            
            # Thực thi tạo tự động bản ghi bên bảng Công việc
            CongViec.create({
                'ten_cong_viec': f"[{self.ten_doi_tac or self.ten_co_hoi}] - {mau.name}",
                'co_hoi_id': self.id,
                'loai_cong_viec': 'gap_mat' if mau.loai_cong_viec in ['khao_sat', 'trien_khai'] else 'goi_dien',
                'nhan_vien_thuc_hien_id': truong_phong.id if truong_phong else False,
                'han_chot': han_chot,
                'do_uu_tien': '2',  # Mặc định gán mức độ ưu tiên Cao cho dự án mới triển khai
                'trang_thai_cong_viec': 'chua_lam',
                'tien_do_phan_tram': 0,
                'ghi_chu': f"Hệ thống tự động điều phối khi chốt thành công cơ hội: {self.ten_co_hoi}."
            })


class KeThemCongViec(models.Model):
    _inherit = 'project.cong.viec'
    
    co_hoi_id = fields.Many2one('crm.co.hoi', string="Khách hàng", ondelete='cascade')