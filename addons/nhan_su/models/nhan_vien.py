from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ho_va_ten'
    _order = 'ten asc, tuoi desc'

    ma_dinh_danh = fields.Char("Mã định danh", required=True, copy=False, readonly=True, default=lambda self: 'Mới')
    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    anh = fields.Binary("Ảnh")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True)
    active = fields.Boolean("Đang hoạt động", default=True)

    don_vi_id = fields.Many2one('don_vi', string="Phòng ban")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    
    user_id = fields.Many2one(
        'res.users', 
        string="Tài khoản đăng nhập", 
        help="Liên kết với tài khoản hệ thống để nhân viên này có quyền đăng nhập và phê duyệt công việc."
    )

    available_user_ids = fields.Many2many(
        'res.users', 
        compute='_compute_available_user_ids', 
        string="Tài khoản khả dụng"
    )

    quan_ly_id = fields.Many2one(
        'nhan_vien', 
        string="Người quản lý trực tiếp",
        domain="[('id', '=', 0)]" 
    )
    
    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Thử việc'),
        ('chinh_thuc', 'Chính thức'),
        ('thoi_vu', 'Thời vụ'), 
        ('bo_nhiem', 'Bổ nhiệm') 
    ], string="Loại hợp đồng", default='thu_viec')
    
    thoi_han_hop_dong = fields.Selection([
        ('1_thang', '01 Tháng'),
        ('2_thang', '02 Tháng (Chuẩn đại học)'),
        ('3_thang', '03 Tháng (Cấp quản lý)'),
        ('12_thang', '12 Tháng (1 năm)'),
        ('24_thang', '24 Tháng (2 năm)'),
        ('36_thang', '36 Tháng (3 năm)'),
        ('vo_thoi_han', 'Không xác định thời hạn')
    ], string="Thời hạn hợp đồng")

    ngay_bat_dau_hd = fields.Date("Ngày bắt đầu HD", default=fields.Date.context_today)
    ngay_ket_thuc_hd = fields.Date("Ngày kết thúc HD", compute="_compute_ngay_ket_thuc_hd", store=True, readonly=False)

    @api.depends('ngay_bat_dau_hd', 'thoi_han_hop_dong')
    def _compute_ngay_ket_thuc_hd(self):
        from dateutil.relativedelta import relativedelta
        for record in self:
            if record.ngay_bat_dau_hd and record.thoi_han_hop_dong:
                if record.thoi_han_hop_dong == '1_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(months=1)
                elif record.thoi_han_hop_dong == '2_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(months=2)
                elif record.thoi_han_hop_dong == '3_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(months=3)
                elif record.thoi_han_hop_dong == '12_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(years=1)
                elif record.thoi_han_hop_dong == '24_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(years=2)
                elif record.thoi_han_hop_dong == '36_thang':
                    record.ngay_ket_thuc_hd = record.ngay_bat_dau_hd + relativedelta(years=3)
                elif record.thoi_han_hop_dong == 'vo_thoi_han':
                    record.ngay_ket_thuc_hd = False
            else:
                record.ngay_ket_thuc_hd = False

    @api.onchange('loai_hop_dong')
    def _onchange_loai_hop_dong(self):
        if self.loai_hop_dong == 'thu_viec':
            self.thoi_han_hop_dong = '2_thang' 
        elif self.loai_hop_dong == 'chinh_thuc':
            self.thoi_han_hop_dong = '12_thang' 
        elif self.loai_hop_dong == 'thoi_vu':
            self.thoi_han_hop_dong = '3_thang' 
        elif self.loai_hop_dong == 'bo_nhiem':
            self.thoi_han_hop_dong = 'vo_thoi_han'

    trang_thai_lam_viec = fields.Selection([
        ('dang_lam', 'Đang làm việc'),
        ('nghi_phep', 'Nghỉ phép dài hạn'),
        ('da_nghi', 'Đã nghỉ việc')
    ], string="Trạng thái làm việc", default='dang_lam')

    lich_su_cong_tac_ids = fields.One2many(
        "lich_su_cong_tac", 
        inverse_name="nhan_vien_id", 
        string="Danh sách lịch sử công tác"
    )
    danh_sach_chung_chi_bang_cap_ids = fields.One2many(
        "danh_sach_chung_chi_bang_cap", 
        inverse_name="nhan_vien_id", 
        string="Danh sách chứng chỉ bằng cấp"
    )
    
    so_nguoi_bang_tuoi = fields.Integer(
        "Số người bằng tuổi", 
        compute="_compute_so_nguoi_bang_tuoi",
        store=True
    )
    
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh phải là duy nhất!')
    ]

    @api.depends("tuoi")
    def _compute_so_nguoi_bang_tuoi(self):
        for record in self:
            if record.tuoi:
                current_id = record._origin.id if isinstance(record.id, models.NewId) else record.id
                records = self.env['nhan_vien'].search([
                    ('tuoi', '=', record.tuoi),
                    ('id', '!=', current_id)
                ])
                record.so_nguoi_bang_tuoi = len(records)
            else:
                record.so_nguoi_bang_tuoi = 0

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = f"{record.ho_ten_dem} {record.ten}"
            else:
                record.ho_va_ten = ""

    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                year_now = date.today().year
                record.tuoi = year_now - record.ngay_sinh.year
            else:
                record.tuoi = 0

    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.ngay_sinh and record.tuoi < 18:
                raise ValidationError("Tuổi không được bé hơn 18")
    
    @api.onchange('don_vi_id', 'chuc_vu_id')
    def _onchange_don_vi_id(self):
        res = {'domain': {}}
        self.quan_ly_id = False
        current_id = self._origin.id if isinstance(self.id, models.NewId) else self.id
        
        if self.don_vi_id:
            if self.don_vi_id.ten_don_vi == 'Hội đồng quản trị':
                res['domain']['quan_ly_id'] = [
                    ('chuc_vu_id.ma_chuc_vu', '=', 'CHAIRMAN'), 
                    ('trang_thai_lam_viec', '=', 'dang_lam'),
                    ('id', '!=', current_id)
                ]
            else:
                chuc_vu_hien_tai = self.chuc_vu_id.ma_chuc_vu if self.chuc_vu_id else ''
                
                if chuc_vu_hien_tai in ['CTO', 'CCO', 'RM']:
                    res['domain']['quan_ly_id'] = [
                        ('don_vi_id.ten_don_vi', '=', 'Hội đồng quản trị'),
                        ('chuc_vu_id.ma_chuc_vu', '=', 'CEO'), 
                        ('trang_thai_lam_viec', '=', 'dang_lam')
                    ]
                elif chuc_vu_hien_tai in ['TPKT', 'TPKD', 'TPCSKH']:
                    res['domain']['quan_ly_id'] = [
                        ('don_vi_id', '=', self.don_vi_id.id),
                        ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Giám đốc'),
                        ('trang_thai_lam_viec', '=', 'dang_lam'),
                        ('id', '!=', current_id)
                    ]
                else:
                    res['domain']['quan_ly_id'] = [
                        ('don_vi_id', '=', self.don_vi_id.id),
                        ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Trưởng'), 
                        ('trang_thai_lam_viec', '=', 'dang_lam'),
                        ('id', '!=', current_id)
                    ]
        else:
            res['domain']['quan_ly_id'] = [
                ('|', ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Trưởng'), ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Giám đốc')),
                ('trang_thai_lam_viec', '=', 'dang_lam'),
                ('id', '!=', current_id)
            ]
        return res
    
    @api.onchange('user_id', 'chuc_vu_id', 'don_vi_id')
    def _onchange_user_id(self):
        """ Gợi ý điền nhanh thông tin liên hệ sang User khi chọn """
        if self.user_id:
            if not self.user_id.login and self.email:
                self.user_id.login = self.email
            if not self.user_id.email and self.email:
                self.user_id.email = self.email
            if hasattr(self.user_id, 'phone') and not self.user_id.phone and self.so_dien_thoai:
                self.user_id.phone = self.so_dien_thoai

    @api.depends('user_id')
    def _compute_available_user_ids(self):
        for record in self:
            current_id = record._origin.id if isinstance(record.id, models.NewId) else record.id
            domain = [('user_id', '!=', False)]
            if current_id:
                domain.append(('id', '!=', current_id))
                
            nhan_vien_da_co_user = self.env['nhan_vien'].search(domain)
            user_ids_da_dung = nhan_vien_da_co_user.mapped('user_id').ids
            
            available_users = self.env['res.users'].search([('id', 'not in', user_ids_da_dung)])
            record.available_user_ids = [(6, 0, available_users.ids)]

    def _sync_user_display_name(self):
        """ Hàm xử lý ép cấu trúc tên hiển thị chi tiết cho res.users """
        for record in self:
            if record.user_id:
                ma = record.ma_dinh_danh or 'Mới'
                ho_ten = f"{record.ho_ten_dem or ''} {record.ten or ''}".strip()
                chuc_vu = record.chuc_vu_id.ten_chuc_vu if record.chuc_vu_id else 'Chưa có chức vụ'
                phong_ban = record.don_vi_id.ten_don_vi if record.don_vi_id else 'Chưa có phòng'
                
                # Ép chuỗi cấu trúc định danh chi tiết
                record.user_id.name = f"[{ma}] {ho_ten} - {chuc_vu} ({phong_ban})"

    @api.model
    def create(self, vals):
        # Tự động sinh mã nhân viên bằng ir.sequence
        if vals.get('ma_dinh_danh', 'Mới') == 'Mới' or not vals.get('ma_dinh_danh'):
            vals['ma_dinh_danh'] = self.env['ir.sequence'].next_by_code('nhan_vien.sequence') or 'Mới'
        
        record = super(NhanVien, self).create(vals)
        # Đồng bộ tên sau khi dữ liệu thô đã được ghi nhận vào database thành công
        record._sync_user_display_name()
        return record

    def write(self, vals):
        res = super(NhanVien, self).write(vals)
        # Nếu có bất kỳ sự thay đổi nào về thông tin định danh, tự động cập nhật lại tên User
        if any(field in vals for field in ['user_id', 'chuc_vu_id', 'don_vi_id', 'ho_ten_dem', 'ten']):
            self._sync_user_display_name()

        # FIX: logic ẩn hồ sơ khi nghỉ việc trước đây CHỈ nằm trong @api.onchange,
        # nên chỉ có hiệu lực khi người dùng thao tác trực tiếp trên form UI.
        # Nếu HR cập nhật trạng thái qua danh sách (list view inline edit), import
        # Excel, hoặc gọi qua API/XML-RPC thì active KHÔNG được cập nhật -> hồ sơ
        # nhân viên đã nghỉ vẫn hiển thị "đang hoạt động" trong các domain lựa chọn
        # (vd. domain chọn nhân_vien_thuc_hien_id bên module Công việc), dẫn tới
        # rủi ro giao việc/khách hàng mới cho người đã nghỉ. Đưa xuống write() để
        # đảm bảo áp dụng cho MỌI đường cập nhật dữ liệu.
        if 'trang_thai_lam_viec' in vals:
            for record in self:
                new_active = record.trang_thai_lam_viec != 'da_nghi'
                if record.active != new_active:
                    record.active = new_active
        return res

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    nhan_vien_ids = fields.One2many('nhan_vien', 'user_id', string="Hồ sơ nhân sự")
    
    # Kéo thông tin Chức vụ và Phòng ban từ hồ sơ nhân sự sang User
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", compute="_compute_hr_info")
    don_vi_id = fields.Many2one('don_vi', string="Phòng ban", compute="_compute_hr_info")

    @api.depends('nhan_vien_ids', 'nhan_vien_ids.chuc_vu_id', 'nhan_vien_ids.don_vi_id')
    def _compute_hr_info(self):
        for user in self:
            if user.nhan_vien_ids:
                # Lấy thông tin của hồ sơ nhân viên đầu tiên liên kết với User này
                user.chuc_vu_id = user.nhan_vien_ids[0].chuc_vu_id.id
                user.don_vi_id = user.nhan_vien_ids[0].don_vi_id.id
            else:
                user.chuc_vu_id = False
                user.don_vi_id = False