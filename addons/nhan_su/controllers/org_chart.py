from odoo import http
from odoo.http import request
import json

class NhanSuOrgChart(http.Controller):
    # Khai báo đường dẫn web sinh ra sơ đồ
    @http.route('/nhan_su/so_do_to_chuc', type='http', auth='user', website=True)
    def render_org_chart(self):
        # Lấy toàn bộ nhân viên đang làm việc
        nhan_viens = request.env['nhan_vien'].sudo().search([('trang_thai_lam_viec', '=', 'dang_lam')])
        
        data = []
        for nv in nhan_viens:
            node_id = str(nv.id)
            # Khóa chính để vẽ đường nối từ lính lên sếp
            manager_id = str(nv.quan_ly_id.id) if nv.quan_ly_id else '' 
            
            ten = nv.ho_va_ten or 'Chưa có tên'
            chuc_vu = nv.chuc_vu_id.ten_chuc_vu if nv.chuc_vu_id else 'Nhân viên'
            phong_ban = nv.don_vi_id.ten_don_vi if nv.don_vi_id else 'Chưa có phòng'
            
            # Thiết kế Card (Thẻ) hiển thị trên sơ đồ tư duy
            html_card = f"""
                <div style="border: 2px solid #3b82f6; border-radius: 8px; padding: 15px; background: #ffffff; width: 180px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); font-family: Arial, sans-serif;">
                    <h4 style="margin: 0; color: #1e3a8a; font-size: 15px; font-weight: bold;">{ten}</h4>
                    <hr style="margin: 8px 0; border: 0; border-top: 1px solid #e5e7eb;"/>
                    <div style="font-size: 12px; color: #059669; font-weight: bold; margin-bottom: 4px;">
                        &#128188; {chuc_vu}
                    </div>
                    <div style="font-size: 11px; color: #4b5563; background: #f3f4f6; padding: 4px; border-radius: 4px;">
                        &#127970; {phong_ban}
                    </div>
                </div>
            """
            
            # Append vào data (Mã id, Mã HTML, Mã người quản lý)
            data.append([{ 'v': node_id, 'f': html_card }, manager_id, ten])

        # Trả về trang HTML nhúng thư viện Google OrgChart
        html_page = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Sơ đồ tổ chức</title>
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
                google.charts.load('current', {packages:['orgchart']});
                google.charts.setOnLoadCallback(drawChart);

                function drawChart() {
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Name');
                    data.addColumn('string', 'Manager');
                    data.addColumn('string', 'ToolTip');

                    // Dữ liệu từ Odoo truyền xuống
                    var rowData = %s;
                    data.addRows(rowData);

                    var chart = new google.visualization.OrgChart(document.getElementById('chart_div'));
                    chart.draw(data, {
                        'allowHtml': true, 
                        'nodeClass': 'customNode',
                        'selectedNodeClass': 'selectedNode'
                    });
                }
            </script>
            <style>
                body { background-color: #f9fafb; margin: 0; padding: 30px; font-family: Arial, sans-serif; }
                .customNode { border: none !important; background: none !important; box-shadow: none !important; padding: 0 !important; cursor: pointer; }
                .selectedNode { border: none !important; background: none !important; transform: scale(1.05); transition: 0.2s; }
                /* Custom màu sắc đường kẻ nối các thẻ */
                .google-visualization-orgchart-linebottom { border-bottom: 3px solid #9ca3af !important; }
                .google-visualization-orgchart-lineright { border-right: 3px solid #9ca3af !important; }
                .google-visualization-orgchart-lineleft { border-left: 3px solid #9ca3af !important; }
                table { border-collapse: separate !important; }
            </style>
        </head>
        <body>
            <h2 style="text-align: center; color: #111827; text-transform: uppercase; margin-bottom: 40px;">
                Cấu trúc Sơ đồ tổ chức Doanh nghiệp
            </h2>
            <div id="chart_div" style="display: flex; justify-content: center; overflow-x: auto; padding-bottom: 50px;"></div>
        </body>
        </html>
        """ % json.dumps(data)
        
        return html_page