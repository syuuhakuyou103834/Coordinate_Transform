"""
主程序入口 - PyQt5版本
整合Cross Section和Map Establish两个功能模块
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar
from core_cross_section import MapDataProcessor
from core_map_establish import MapEstablishProcessor
from core_fine_map_revision import FineMapRevisionProcessor
import sys


class MainWindow(QMainWindow):
    """主窗口 - 集成Cross Section、Map Establish和Fine Map Revision功能"""

    def __init__(self):
        super().__init__()

        # 初始化核心处理器
        self.cross_section_processor = MapDataProcessor()
        self.map_establish_processor = MapEstablishProcessor()
        self.fine_map_revision_processor = FineMapRevisionProcessor()

        # 延迟导入UI模块（在QApplication创建之后）
        self.cross_section_ui = None
        self.map_establish_ui = None
        self.fine_map_revision_ui = None

        # 设置主窗口
        self._setup_main_window()

        # 创建子窗口UI
        self._create_ui_windows()

    def _create_ui_windows(self):
        """创建UI窗口（必须在QApplication创建之后调用）"""
        from ui_cross_section import MapDataUI
        from ui_map_establish import MapEstablishUI
        from ui_fine_map_revision import FineMapRevisionUI

        # 初始化子窗口UI
        self.cross_section_ui = MapDataUI()
        self.map_establish_ui = MapEstablishUI()
        self.fine_map_revision_ui = FineMapRevisionUI()

        # 设置Cross Section回调
        self.cross_section_ui.set_callbacks(
            load_file=self.load_file,
            search_x=self.search_x,
            search_y=self.search_y
        )

        # 设置Map Establish回调
        self.map_establish_ui.set_callbacks(
            preview=self.preview_map,
            generate=self.generate_map
        )

        # 设置Fine Map Revision回调和处理器
        self.fine_map_revision_ui.set_processor(self.fine_map_revision_processor)
        self.fine_map_revision_ui.set_callbacks(
            import_csv=self.import_fine_map_csv,
            generate_map=self.generate_fine_map,
            update_point=self.update_fine_map_point,
            delete_point=self.delete_fine_map_point,
            add_point=self.add_fine_map_point,
            save_csv=self.save_fine_map_csv
        )

        # 显示三个子窗口
        self.cross_section_ui.show()
        self.map_establish_ui.show()
        self.fine_map_revision_ui.show()

    def _setup_main_window(self):
        """设置主窗口"""
        self.setWindowTitle("地图坐标系统 - v2.2 (新增Fine Map Revision)")
        self.setMinimumSize(400, 300)

        # 创建菜单栏
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件')

        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close_all)
        file_menu.addAction(exit_action)

        # 窗口菜单
        window_menu = menubar.addMenu('窗口')

        cs_action = QAction('Cross Section查询', self)
        cs_action.triggered.connect(self.show_cross_section)
        window_menu.addAction(cs_action)

        me_action = QAction('Map建立工具', self)
        me_action.triggered.connect(self.show_map_establish)
        window_menu.addAction(me_action)

        fmr_action = QAction('精细Map修订', self)
        fmr_action.triggered.connect(self.show_fine_map_revision)
        window_menu.addAction(fmr_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 状态栏
        self.statusBar().showMessage('就绪')

    def show_cross_section(self):
        """显示Cross Section窗口"""
        if self.cross_section_ui:
            self.cross_section_ui.show()
            self.cross_section_ui.raise_()
            self.cross_section_ui.activateWindow()

    def show_map_establish(self):
        """显示Map Establish窗口"""
        if self.map_establish_ui:
            self.map_establish_ui.show()
            self.map_establish_ui.raise_()
            self.map_establish_ui.activateWindow()

    def show_fine_map_revision(self):
        """显示Fine Map Revision窗口"""
        if self.fine_map_revision_ui:
            self.fine_map_revision_ui.show()
            self.fine_map_revision_ui.raise_()
            self.fine_map_revision_ui.activateWindow()

    def show_about(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "关于",
                         "地图坐标查询系统 v2.2\n\n"
                         "功能模块:\n"
                         "1. Cross Section查询 - 坐标查询和膜厚分析\n"
                         "2. Map建立工具 - 晶圆Map生成\n"
                         "3. 精细Map修订 - Map可视化编辑和修订\n\n"
                         "开发环境: Python + PyQt5")

    def close_all(self):
        """关闭所有窗口"""
        if self.cross_section_ui:
            self.cross_section_ui.close()
        if self.map_establish_ui:
            self.map_establish_ui.close()
        if self.fine_map_revision_ui:
            self.fine_map_revision_ui.close()
        QApplication.instance().quit()

    # ========== Cross Section 回调函数 ==========

    def load_file(self, file_path: str) -> bool:
        """
        加载CSV文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 加载成功返回True
        """
        success = self.cross_section_processor.load_csv(file_path)
        if success:
            # 更新数据摘要显示
            summary = self.cross_section_processor.get_data_summary()
            self.cross_section_ui.set_data_summary(summary)
        return success

    def search_x(self, x_value: float) -> list:
        """
        根据X坐标搜索

        Args:
            x_value: X坐标值

        Returns:
            list: 查询结果列表
        """
        return self.cross_section_processor.search_by_x(x_value)

    def search_y(self, y_value: float) -> list:
        """
        根据Y坐标搜索

        Args:
            y_value: Y坐标值

        Returns:
            list: 查询结果列表
        """
        return self.cross_section_processor.search_by_y(y_value)

    # ========== Map Establish 回调函数 ==========

    def preview_map(self, wafer_size: str, ref_x: float, ref_y: float,
                   x_pitch: float, y_pitch: float, start_position: str,
                   scan_direction: str):
        """
        预览Map

        Args:
            wafer_size: 晶圆尺寸
            ref_x: 参考点X坐标
            ref_y: 参考点Y坐标
            x_pitch: X方向间距
            y_pitch: Y方向间距
            start_position: 起点位置
            scan_direction: 扫描方向

        Returns:
            Tuple: (扫描路径, 统计信息)
        """
        return self.map_establish_processor.generate_map_data(
            wafer_size, ref_x, ref_y, x_pitch, y_pitch,
            start_position, scan_direction
        )

    def generate_map(self, scan_path: list, file_path: str,
                    x_pitch_str: str, y_pitch_str: str) -> bool:
        """
        生成Map CSV文件

        Args:
            scan_path: 扫描路径
            file_path: 保存文件路径
            x_pitch_str: X方向间距字符串（用于确定精度）
            y_pitch_str: Y方向间距字符串（用于确定精度）

        Returns:
            bool: 成功返回True
        """
        # 从字符串中确定小数位数
        def get_decimal_places(s: str) -> int:
            if '.' in s:
                return len(s.split('.')[1].rstrip('0'))
            return 0

        x_decimal = get_decimal_places(x_pitch_str)
        y_decimal = get_decimal_places(y_pitch_str)
        decimal_places = max(x_decimal, y_decimal)

        return self.map_establish_processor.save_to_csv(
            scan_path, file_path, decimal_places
        )

    # ========== Fine Map Revision 回调函数 ==========

    def import_fine_map_csv(self, file_path: str) -> bool:
        """
        导入Fine Map CSV文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 成功返回True
        """
        print(f"\n[Main Callback] import_fine_map_csv() 调用")
        print(f"  文件路径: '{file_path}'")
        result = self.fine_map_revision_processor.load_from_csv(file_path)
        print(f"[Main Callback] import_fine_map_csv() 返回: {result}")
        return result

    def generate_fine_map(self, x_length: float, y_length: float,
                         x_pitch: float, y_pitch: float,
                         center_x: float, center_y: float) -> bool:
        """
        生成新的Fine Map

        Args:
            x_length: X方向长度
            y_length: Y方向长度
            x_pitch: X方向间距
            y_pitch: Y方向间距
            center_x: 中心点X坐标
            center_y: 中心点Y坐标

        Returns:
            bool: 成功返回True
        """
        print(f"\n[Main Callback] generate_fine_map() 调用")
        print(f"  参数: x_length={x_length:.4f}, y_length={y_length:.4f}")
        print(f"       x_pitch={x_pitch:.4f}, y_pitch={y_pitch:.4f}")
        print(f"       center=({center_x:.4f}, {center_y:.4f})")
        result = self.fine_map_revision_processor.generate_rectangular_map(
            x_length, y_length, x_pitch, y_pitch, center_x, center_y
        )
        print(f"[Main Callback] generate_fine_map() 返回: {result}")
        return result

    def update_fine_map_point(self, index: int, x: float, y: float) -> bool:
        """
        更新Fine Map中的点

        Args:
            index: 点的索引
            x: 新的X坐标
            y: 新的Y坐标

        Returns:
            bool: 成功返回True
        """
        print(f"\n[Main Callback] update_fine_map_point() 调用")
        print(f"  索引: {index}, 新坐标: ({x:.4f}, {y:.4f})")
        result = self.fine_map_revision_processor.update_point(index, x, y)
        print(f"[Main Callback] update_fine_map_point() 返回: {result}")
        return result

    def delete_fine_map_point(self, index: int) -> bool:
        """
        删除Fine Map中的点

        Args:
            index: 点的索引

        Returns:
            bool: 成功返回True
        """
        print(f"\n[Main Callback] delete_fine_map_point() 调用")
        print(f"  索引: {index}")
        result = self.fine_map_revision_processor.delete_point(index)
        print(f"[Main Callback] delete_fine_map_point() 返回: {result}")
        return result

    def add_fine_map_point(self, x: float, y: float):
        """
        添加点到Fine Map

        Args:
            x: X坐标
            y: Y坐标
        """
        print(f"\n[Main Callback] add_fine_map_point() 调用")
        print(f"  坐标: ({x:.4f}, {y:.4f})")
        self.fine_map_revision_processor.add_point(x, y)
        print(f"[Main Callback] add_fine_map_point() 完成")

    def save_fine_map_csv(self, file_path: str) -> bool:
        """
        保存Fine Map到CSV文件

        Args:
            file_path: 保存路径

        Returns:
            bool: 成功返回True
        """
        print(f"\n[Main Callback] save_fine_map_csv() 调用")
        print(f"  保存路径: '{file_path}'")
        # 默认保留6位小数
        result = self.fine_map_revision_processor.save_to_csv(file_path, 6)
        print(f"[Main Callback] save_fine_map_csv() 返回: {result}")
        return result


def main():
    """主函数"""
    # 必须首先创建QApplication
    app = QApplication(sys.argv)

    # 然后创建主窗口
    window = MainWindow()
    window.show()

    # 运行事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
