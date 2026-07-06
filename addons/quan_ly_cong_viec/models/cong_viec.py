from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DuAn(models.Model):
    """BỔ SUNG: lớp Dự án để nhóm các đầu việc (Task) lại theo từng khách hàng/
    hợp đồng/chiến dịch, đáp ứng đúng yêu cầu 'hệ thống Quản lý dự án + Quản lý
    công việc liên kết với HRM'. Trước đây module chỉ có Task rời rạc, không có
    lớp cha để quản lý theo phòng ban / người phụ trách tổng thể."""
    _name = 'project.du_an'
    _description = 'Dự án / Chiến dịch chăm sóc khách hàng'
    _rec_name = 'ten_du_an'

    ten_du_an = fields.Char("Tên dự án", required=True)
    don_vi_id = fields.Many2one('don_vi', string="Phòng ban phụ trách")
    nguoi_phu_trach_id = fields.Many2one(
        'nhan_vien', string="Người phụ trách dự án",
        domain="[('trang_thai_lam_viec', '=', 'dang_lam')]"
    )
    ngay_bat_dau = fields.Date("Ngày bắt đầu", default=fields.Date.context_today)
    han_chot = fields.Date("Hạn chót dự án")
    trang_thai = fields.Selection([
        ('dang_trien_khai', 'Đang triển khai'),
        ('hoan_thanh', 'Hoàn thành'),
        ('tam_dung', 'Tạm dừng'),
    ], string="Trạng thái", default='dang_trien_khai')
    mo_ta = fields.Text("Mô tả")

    cong_viec_ids = fields.One2many('project.cong.viec', 'du_an_id', string="Công việc thuộc dự án")

    # Các chỉ số tổng hợp giúp quản lý biết ngay: ai đang làm gì, việc nào trễ,
    # tiến độ chung ra sao - trả lời trực tiếp bài toán doanh nghiệp nêu ra.
    so_luong_cong_viec = fields.Integer("Tổng số việc", compute="_compute_thong_ke")
    so_viec_qua_han = fields.Integer("Số việc quá hạn", compute="_compute_thong_ke")
    ty_le_hoan_thanh = fields.Float("Tỷ lệ hoàn thành (%)", compute="_compute_thong_ke")

    @api.depends('cong_viec_ids.trang_thai_cong_viec', 'cong_viec_ids.han_chot')
    def _compute_thong_ke(self):
        today = fields.Date.context_today(self)
        for du_an in self:
            tasks = du_an.cong_viec_ids
            du_an.so_luong_cong_viec = len(tasks)
            du_an.so_viec_qua_han = len(tasks.filtered(
                lambda t: t.han_chot and t.han_chot < today and t.trang_thai_cong_viec not in ('hoan_thanh', 'huy')
            ))
            hoan_thanh = len(tasks.filtered(lambda t: t.trang_thai_cong_viec == 'hoan_thanh'))
            du_an.ty_le_hoan_thanh = (hoan_thanh / len(tasks) * 100) if tasks else 0.0


class CongViecChamSoc(models.Model):
    _name = 'project.cong.viec'
    _description = 'Bảng chứa các đầu việc chăm sóc khách hàng'
    _rec_name = 'ten_cong_viec'
    # BỔ SUNG mail.thread/mail.activity.mixin: cần thiết để dùng message_post()
    # và activity_schedule() trong cron nhắc nhở quá hạn (Fix Rủi ro #1).
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # 1. Thông tin chung
    ten_cong_viec = fields.Char("Tên đầu việc", required=True)
    # BỔ SUNG: field active - trước đây model không có field này nên KHÔNG hỗ
    # trợ lưu trữ (archive); mọi lệnh xoá (kể cả bấm 🗑 trong list nhúng bên
    # CRM) đều là xoá vĩnh viễn. Hậu quả: nếu task đã có activity/message gắn
    # vào (ví dụ do cron nhắc quá hạn, hoặc do luồng phê duyệt tạo) mà bị xoá
    # thẳng, activity đó thành "mồ côi" - trỏ tới 1 record không còn tồn tại,
    # gây lỗi "Missing Record" mỗi khi Odoo cố hiển thị nó (ví dụ chuông
    # Activities). Thêm active + override unlink() để xoá = ẩn thay vì xoá
    # thật, giữ nguyên vẹn activity/message liên quan.
    active = fields.Boolean("Đang hoạt động", default=True)
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
    nhan_vien_thuc_hien_id = fields.Many2one(
        'nhan_vien', string="Người thực hiện",
        domain="[('trang_thai_lam_viec', '=', 'dang_lam')]",
        help="Chỉ được chọn nhân viên đang làm việc từ danh sách gốc HRM,"
             " không tự tạo nhân viên riêng ở module này."
    )
    du_an_id = fields.Many2one('project.du_an', string="Thuộc dự án")

    # BỔ SUNG: cờ nhắc trễ hạn, dùng cho cron nhắc nhở (Fix Rủi ro #1 - nhân viên
    # không tự cập nhật tiến độ). True nghĩa là đã gửi nhắc nhở cho lần quá hạn
    # này rồi, tránh gửi lặp lại thông báo mỗi ngày cho cùng một task.
    da_nhac_qua_han = fields.Boolean("Đã nhắc quá hạn", default=False, copy=False)

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

    def write(self, vals):
        # Người dùng vừa cập nhật hạn chót hoặc trạng thái -> coi như task đã
        # được "chạm tới", reset cờ nhắc trễ hạn để chu kỳ quá hạn tiếp theo
        # (nếu có) vẫn được cron nhắc nhở lại bình thường.
        if 'han_chot' in vals or 'trang_thai_cong_viec' in vals:
            vals.setdefault('da_nhac_qua_han', False)
        return super().write(vals)

    def unlink(self):
        # FIX: chặn xoá vĩnh viễn để không tạo activity/message mồ côi (xem
        # ghi chú ở field `active`). Bấm 🗑 giờ chỉ ẩn task (active=False),
        # không còn hiện trong danh sách/kanban/dashboard nhưng lịch sử vẫn
        # còn nguyên, activity/message vẫn resolve được bình thường.
        self.write({'active': False})
        return True

    # ==================== FIX RỦI RO #1: NV KHÔNG CẬP NHẬT TIẾN ĐỘ ====================
    @api.model
    def _cron_nhac_nho_qua_han(self):
        """ Cron chạy hàng ngày: quét các task quá hạn mà nhân viên chưa hoàn
        thành và CHƯA từng được nhắc, gửi thông báo (activity) cho cả nhân viên
        thực hiện và Trưởng phòng của họ. Giải quyết đúng rủi ro: 'Nhân viên
        kinh doanh trao đổi qua Zalo/điện thoại nhưng không cập nhật hệ thống,
        khiến báo cáo KPI trống và quản lý không theo dõi được'. """
        today = fields.Date.context_today(self)
        qua_han = self.search([
            ('han_chot', '<', today),
            ('trang_thai_cong_viec', 'not in', ['hoan_thanh', 'huy']),
            ('da_nhac_qua_han', '=', False),
        ])
        for task in qua_han:
            nguoi_nhan = task.nhan_vien_thuc_hien_id
            noi_dung = (
                f"Công việc '{task.ten_cong_viec}' đã quá hạn chót ({task.han_chot})"
                f" nhưng vẫn ở trạng thái '{dict(task._fields['trang_thai_cong_viec'].selection).get(task.trang_thai_cong_viec)}'."
                " Vui lòng cập nhật tiến độ trên hệ thống."
            )
            task.message_post(body=noi_dung)
            if nguoi_nhan and nguoi_nhan.user_id:
                task.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary="Công việc quá hạn - cần cập nhật tiến độ",
                    note=noi_dung,
                    user_id=nguoi_nhan.user_id.id,
                )
            # Đồng thời báo cho Trưởng phòng của đơn vị để kịp giám sát/điều phối
            if nguoi_nhan and nguoi_nhan.don_vi_id:
                truong_phong = self.env['nhan_vien'].search([
                    ('don_vi_id', '=', nguoi_nhan.don_vi_id.id),
                    ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Trưởng'),
                    ('trang_thai_lam_viec', '=', 'dang_lam'),
                ], limit=1)
                if truong_phong and truong_phong.user_id:
                    task.activity_schedule(
                        'mail.mail_activity_data_todo',
                        summary=f"[Giám sát] Việc quá hạn của {nguoi_nhan.ho_va_ten}",
                        note=noi_dung,
                        user_id=truong_phong.user_id.id,
                    )
        qua_han.write({'da_nhac_qua_han': True})


class NhanVienBoSungQuanLyCongViec(models.Model):
    """BỔ SUNG (trong module Quản lý công việc, KHÔNG sửa module HRM gốc):
    kế thừa nhan_vien để thêm các chỉ số 'quá tải' và cơ chế tự động chuyển
    giao công việc khi nhân viên nghỉ việc - giải quyết đúng bài toán doanh
    nghiệp 'quản lý khó biết nhân viên nào quá tải' và rủi ro 'thất lạc lịch
    sử công việc khi nhân viên nghỉ'."""
    _inherit = 'nhan_vien'

    NGUONG_QUA_TAI = 10  # số việc đang xử lý đồng thời được coi là quá tải

    so_cong_viec_dang_xu_ly = fields.Integer(
        "Số việc đang xử lý", compute="_compute_tinh_trang_cong_viec"
    )
    so_cong_viec_qua_han = fields.Integer(
        "Số việc quá hạn", compute="_compute_tinh_trang_cong_viec"
    )
    canh_bao_qua_tai = fields.Boolean(
        "Cảnh báo quá tải", compute="_compute_tinh_trang_cong_viec"
    )

    def _compute_tinh_trang_cong_viec(self):
        Task = self.env['project.cong.viec']
        today = fields.Date.context_today(self)
        for nv in self:
            dang_xu_ly = Task.search([
                ('nhan_vien_thuc_hien_id', '=', nv.id),
                ('trang_thai_cong_viec', 'in', ['chua_lam', 'dang_lam']),
            ])
            nv.so_cong_viec_dang_xu_ly = len(dang_xu_ly)
            nv.so_cong_viec_qua_han = len(dang_xu_ly.filtered(
                lambda t: t.han_chot and t.han_chot < today
            ))
            nv.canh_bao_qua_tai = len(dang_xu_ly) > nv.NGUONG_QUA_TAI

    def write(self, vals):
        res = super().write(vals)
        # FIX: khi HR chuyển trạng thái nhân viên sang "Đã nghỉ việc", các task
        # đang làm/chưa làm của họ KHÔNG được để trống người thực hiện (dễ thất
        # lạc, không ai theo dõi tiếp) mà phải tự động chuyển cho Trưởng phòng
        # của đúng phòng ban đó xử lý/phân công lại - đảm bảo lịch sử & trách
        # nhiệm công việc được bảo toàn liên tục.
        if vals.get('trang_thai_lam_viec') == 'da_nghi':
            Task = self.env['project.cong.viec']
            for nv in self:
                viec_con_mo = Task.search([
                    ('nhan_vien_thuc_hien_id', '=', nv.id),
                    ('trang_thai_cong_viec', 'in', ['chua_lam', 'dang_lam']),
                ])
                if not viec_con_mo:
                    continue
                truong_phong = self.env['nhan_vien'].search([
                    ('don_vi_id', '=', nv.don_vi_id.id),
                    ('chuc_vu_id.ten_chuc_vu', 'ilike', 'Trưởng'),
                    ('trang_thai_lam_viec', '=', 'dang_lam'),
                    ('id', '!=', nv.id),
                ], limit=1)
                viec_con_mo.write({'nhan_vien_thuc_hien_id': truong_phong.id if truong_phong else False})
                viec_con_mo.message_post(
                    body=f"Tự động chuyển giao do nhân viên {nv.ho_va_ten} đã nghỉ việc."
                         + (f" Người nhận mới: {truong_phong.ho_va_ten}." if truong_phong else
                            " CHƯA tìm được Trưởng phòng phù hợp - cần Admin phân công tay.")
                )
        return res