"""
Fine Map Revision UI界面模块
提供交互式可视化编辑界面
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QGroupBox, QSplitter, QDialog, QFormLayout, QDoubleSpinBox,
    QAbstractItemView, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, QSize, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QWheelEvent,
    QMouseEvent, QKeyEvent, QPainterPath
)
from typing import Optional, Callable, List, Tuple
import math


class MapViewWidget(QWidget):
    """交互式Map可视化组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []

        # 视图参数
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.center_x = 0.0
        self.center_y = 0.0

        # 交互状态
        self.last_mouse_pos = QPointF()
        self.is_panning = False
        self.selected_index = None
        self.hover_index = None

        # 回调
        self.on_point_selected = None
        self.on_point_double_clicked = None

        # 设置鼠标追踪
        self.setMouseTracking(True)
        self.setMinimumSize(400, 400)

    def set_points(self, points: List[Tuple[float, float]], center_x: float, center_y: float):
        """设置显示的点"""
        self.points = points
        self.center_x = center_x
        self.center_y = center_y
        self.selected_index = None
        self.hover_index = None
        self.update()

    def set_selected_index(self, index: Optional[int]):
        """设置选中的点"""
        self.selected_index = index
        self.update()

    def get_selected_index(self) -> Optional[int]:
        """获取选中的点索引"""
        return self.selected_index

    def reset_view(self):
        """重置视图到初始状态"""
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.update()

    def world_to_screen(self, x: float, y: float) -> QPointF:
        """世界坐标转屏幕坐标"""
        # 获取组件中心
        widget_center_x = self.width() / 2.0
        widget_center_y = self.height() / 2.0

        # 缩放和平移
        screen_x = widget_center_x + (x - self.center_x) * self.scale_factor + self.offset_x
        screen_y = widget_center_y - (y - self.center_y) * self.scale_factor + self.offset_y

        return QPointF(screen_x, screen_y)

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """屏幕坐标转世界坐标"""
        widget_center_x = self.width() / 2.0
        widget_center_y = self.height() / 2.0

        # 反向转换
        world_x = self.center_x + (screen_x - widget_center_x - self.offset_x) / self.scale_factor
        world_y = self.center_y - (screen_y - widget_center_y - self.offset_y) / self.scale_factor

        return (world_x, world_y)

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 填充背景
        painter.fillRect(self.rect(), QColor(245, 245, 245))

        if not self.points:
            # 显示提示文字
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "请导入或新建Map数据")
            return

        # 绘制网格
        self._draw_grid(painter)

        # 绘制坐标轴
        self._draw_axes(painter)

        # 绘制点
        self._draw_points(painter)

        # 绘制信息
        self._draw_info(painter)

    def _draw_grid(self, painter: QPainter):
        """绘制网格"""
        # 根据缩放级别调整网格间距
        grid_spacing_world = 10.0
        if self.scale_factor < 0.5:
            grid_spacing_world = 50.0
        elif self.scale_factor < 2.0:
            grid_spacing_world = 10.0
        else:
            grid_spacing_world = 5.0

        # 计算屏幕上的网格间距
        grid_spacing_screen = grid_spacing_world * self.scale_factor

        # 网格太密就不绘制
        if grid_spacing_screen < 20:
            return

        painter.setPen(QPen(QColor(220, 220, 220), 1))

        # 获取可见范围
        visible_world_tl = self.screen_to_world(0, 0)
        visible_world_br = self.screen_to_world(self.width(), self.height())

        # 绘制垂直线
        start_x = int(visible_world_tl[0] // grid_spacing_world) * grid_spacing_world
        for x in range(int(start_x), int(visible_world_br[0]) + int(grid_spacing_world), int(grid_spacing_world)):
            p1 = self.world_to_screen(x, visible_world_tl[1])
            p2 = self.world_to_screen(x, visible_world_br[1])
            painter.drawLine(int(p1.x()), int(p1.y()), int(p2.x()), int(p2.y()))

        # 绘制水平线
        start_y = int(visible_world_br[1] // grid_spacing_world) * grid_spacing_world
        for y in range(int(start_y), int(visible_world_tl[1]) + int(grid_spacing_world), int(grid_spacing_world)):
            p1 = self.world_to_screen(visible_world_tl[0], y)
            p2 = self.world_to_screen(visible_world_br[0], y)
            painter.drawLine(int(p1.x()), int(p1.y()), int(p2.x()), int(p2.y()))

    def _draw_axes(self, painter: QPainter):
        """绘制坐标轴"""
        painter.setPen(QPen(QColor(100, 100, 100), 2))

        # X轴
        origin_screen = self.world_to_screen(0, 0)
        x_axis_end = self.world_to_screen(1000, 0)
        painter.drawLine(int(origin_screen.x()), int(origin_screen.y()),
                        int(min(x_axis_end.x(), self.width() * 2)), int(origin_screen.y()))

        # Y轴
        y_axis_end = self.world_to_screen(0, 1000)
        painter.drawLine(int(origin_screen.x()), int(origin_screen.y()),
                        int(origin_screen.x()), int(min(y_axis_end.y(), self.height() * 2)))

        # 绘制刻度和标签
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QColor(80, 80, 80))

        # X轴刻度
        for x in range(-1000, 1001, 50):
            p = self.world_to_screen(x, 0)
            if 0 <= p.x() <= self.width():
                painter.drawLine(int(p.x()), int(origin_screen.y()), int(p.x()), int(origin_screen.y() + 5))
                painter.drawText(int(p.x() - 15), int(origin_screen.y() + 18), str(x))

        # Y轴刻度
        for y in range(-1000, 1001, 50):
            p = self.world_to_screen(0, y)
            if 0 <= p.y() <= self.height():
                painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5), int(p.y()))
                painter.drawText(int(origin_screen.x() - 35), int(p.y() + 4), str(y))

    def _draw_points(self, painter: QPainter):
        """绘制点"""
        for i, (x, y) in enumerate(self.points):
            screen_pos = self.world_to_screen(x, y)

            # 检查是否在可见范围内
            if not (-50 <= screen_pos.x() <= self.width() + 50 and -50 <= screen_pos.y() <= self.height() + 50):
                continue

            # 绘制点
            if i == self.selected_index:
                # 选中点: 红色大圆
                painter.setBrush(QBrush(QColor(255, 0, 0)))
                painter.setPen(QPen(QColor(200, 0, 0), 2))
                radius = 8
            elif i == self.hover_index:
                # 悬停点: 橙色中圆
                painter.setBrush(QBrush(QColor(255, 165, 0)))
                painter.setPen(QPen(QColor(200, 120, 0), 1))
                radius = 6
            else:
                # 普通点: 蓝色小圆
                painter.setBrush(QBrush(QColor(0, 120, 255)))
                painter.setPen(QPen(QColor(0, 80, 200), 1))
                radius = 4

            painter.drawEllipse(screen_pos, radius, radius)

    def _draw_info(self, painter: QPainter):
        """绘制信息"""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.points):
            x, y = self.points[self.selected_index]
            info = f"选中点 [{self.selected_index}]: ({x:.2f}, {y:.2f})"
            painter.setPen(QColor(50, 50, 50))
            painter.setFont(QFont("Arial", 10))
            painter.drawText(10, 20, info)

        # 绘制缩放信息
        zoom_info = f"缩放: {self.scale_factor:.2f}x"
        painter.drawText(10, self.height() - 10, zoom_info)

    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放"""
        # 获取鼠标位置
        mouse_pos = event.pos()
        world_pos_before = self.screen_to_world(mouse_pos.x(), mouse_pos.y())

        # 计算缩放
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        new_scale = self.scale_factor * zoom_factor

        # 限制缩放范围 (0.1x 到 50.0x)
        if 0.1 <= new_scale <= 50.0:
            self.scale_factor = new_scale

            # 调整偏移,使鼠标位置保持不变
            world_pos_after = self.screen_to_world(mouse_pos.x(), mouse_pos.y())
            self.offset_x += (world_pos_after[0] - world_pos_before[0]) * self.scale_factor
            self.offset_y -= (world_pos_after[1] - world_pos_before[1]) * self.scale_factor

            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            # 查找最近的点
            mouse_pos = event.pos()
            world_pos = self.screen_to_world(mouse_pos.x(), mouse_pos.y())

            nearest = self._find_nearest_point(world_pos[0], world_pos[1], threshold=10.0 / self.scale_factor)

            if nearest is not None:
                # 选中点
                self.selected_index = nearest
                if self.on_point_selected:
                    self.on_point_selected(nearest)
            else:
                # 开始平移
                self.is_panning = True
                self.last_mouse_pos = event.localPos()

            self.update()

        elif event.button() == Qt.RightButton:
            # 右键菜单
            self._show_context_menu(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动"""
        # 更新悬停点
        mouse_pos = event.pos()
        world_pos = self.screen_to_world(mouse_pos.x(), mouse_pos.y())

        if not self.is_panning:
            nearest = self._find_nearest_point(world_pos[0], world_pos[1], threshold=10.0 / self.scale_factor)
            self.hover_index = nearest
            self.update()

        # 平移
        if self.is_panning:
            delta = event.localPos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.localPos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放"""
        if event.button() == Qt.LeftButton:
            self.is_panning = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击事件"""
        if event.button() == Qt.LeftButton and self.on_point_double_clicked:
            mouse_pos = event.pos()
            world_pos = self.screen_to_world(mouse_pos.x(), mouse_pos.y())

            nearest = self._find_nearest_point(world_pos[0], world_pos[1], threshold=10.0 / self.scale_factor)

            if nearest is not None:
                self.on_point_double_clicked(nearest)

    def _find_nearest_point(self, x: float, y: float, threshold: float) -> Optional[int]:
        """查找最近的点"""
        if not self.points:
            return None

        min_dist = float('inf')
        nearest = None

        for i, (px, py) in enumerate(self.points):
            dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest = i

        if min_dist <= threshold:
            return nearest
        return None

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        add_action = QAction("添加点", self)
        add_action.triggered.connect(lambda: self._add_point_at(pos))
        menu.addAction(add_action)

        if self.selected_index is not None:
            delete_action = QAction("删除选中点", self)
            delete_action.triggered.connect(self._delete_selected_point)
            menu.addAction(delete_action)

        reset_view_action = QAction("重置视图", self)
        reset_view_action.triggered.connect(self.reset_view)
        menu.addAction(reset_view_action)

        menu.exec_(self.mapToGlobal(pos))

    def _add_point_at(self, pos):
        """在指定位置添加点"""
        world_pos = self.screen_to_world(pos.x(), pos.y())
        if self.on_point_selected:
            # 通过回调通知添加点(这里复用选中回调,实际由UI处理)
            self.on_point_selected((-1, world_pos[0], world_pos[1]))  # -1 表示添加

    def _delete_selected_point(self):
        """删除选中的点"""
        if self.selected_index is not None and self.on_point_selected:
            self.on_point_selected((-2, 0, 0))  # -2 表示删除


class NewMapDialog(QDialog):
    """新建Map对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建Map")
        self.setMinimumWidth(400)

        layout = QFormLayout()

        # X方向长度
        self.x_length_spin = QDoubleSpinBox()
        self.x_length_spin.setRange(0.1, 1000.0)
        self.x_length_spin.setValue(140.0)
        self.x_length_spin.setSuffix(" mm")
        self.x_length_spin.setDecimals(2)
        layout.addRow("X方向长度:", self.x_length_spin)

        # Y方向长度
        self.y_length_spin = QDoubleSpinBox()
        self.y_length_spin.setRange(0.1, 1000.0)
        self.y_length_spin.setValue(140.0)
        self.y_length_spin.setSuffix(" mm")
        self.y_length_spin.setDecimals(2)
        layout.addRow("Y方向长度:", self.y_length_spin)

        # X方向间距
        self.x_pitch_spin = QDoubleSpinBox()
        self.x_pitch_spin.setRange(0.1, 100.0)
        self.x_pitch_spin.setValue(2.0)
        self.x_pitch_spin.setSuffix(" mm")
        self.x_pitch_spin.setDecimals(2)
        layout.addRow("X方向间距:", self.x_pitch_spin)

        # Y方向间距
        self.y_pitch_spin = QDoubleSpinBox()
        self.y_pitch_spin.setRange(0.1, 100.0)
        self.y_pitch_spin.setValue(2.0)
        self.y_pitch_spin.setSuffix(" mm")
        self.y_pitch_spin.setDecimals(2)
        layout.addRow("Y方向间距:", self.y_pitch_spin)

        # 中心点X坐标
        self.center_x_spin = QDoubleSpinBox()
        self.center_x_spin.setRange(-500.0, 500.0)
        self.center_x_spin.setValue(0.0)
        self.center_x_spin.setSuffix(" mm")
        self.center_x_spin.setDecimals(2)
        layout.addRow("中心点X坐标:", self.center_x_spin)

        # 中心点Y坐标
        self.center_y_spin = QDoubleSpinBox()
        self.center_y_spin.setRange(-500.0, 500.0)
        self.center_y_spin.setValue(0.0)
        self.center_y_spin.setSuffix(" mm")
        self.center_y_spin.setDecimals(2)
        layout.addRow("中心点Y坐标:", self.center_y_spin)

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

        self.setLayout(layout)

    def get_parameters(self) -> Tuple[float, float, float, float, float, float]:
        """获取参数"""
        return (
            self.x_length_spin.value(),
            self.y_length_spin.value(),
            self.x_pitch_spin.value(),
            self.y_pitch_spin.value(),
            self.center_x_spin.value(),
            self.center_y_spin.value()
        )


class FineMapRevisionUI(QMainWindow):
    """精细Map修订UI界面"""

    def __init__(self):
        super().__init__()
        self.processor = None  # 核心处理器(由主程序设置)

        # 回调函数
        self.on_import_csv = None
        self.on_generate_map = None
        self.on_update_point = None
        self.on_delete_point = None
        self.on_add_point = None
        self.on_save_csv = None

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        self.setWindowTitle("精细Map修订工具")
        self.setMinimumSize(1400, 800)

        # 创建主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 菜单栏
        menubar = self.menuBar()
        data_menu = menubar.addMenu("数据")

        import_action = QAction("导入现有Map", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_csv)
        data_menu.addAction(import_action)

        new_action = QAction("新建Map", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_map)
        data_menu.addAction(new_action)

        data_menu.addSeparator()

        save_action = QAction("保存到CSV", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_csv)
        data_menu.addAction(save_action)

        # 使用Splitter分割左右区域
        splitter = QSplitter(Qt.Horizontal)

        # 左侧: 可视化视图
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        view_group = QGroupBox("Map可视化")
        view_layout = QVBoxLayout()

        self.map_view = MapViewWidget()
        self.map_view.on_point_selected = self._on_point_selected
        self.map_view.on_point_double_clicked = self._on_point_double_clicked

        view_layout.addWidget(self.map_view)
        view_group.setLayout(view_layout)

        left_layout.addWidget(view_group)

        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout()

        reset_view_btn = QPushButton("重置视图")
        reset_view_btn.clicked.connect(self.map_view.reset_view)
        control_layout.addWidget(reset_view_btn)

        edit_btn = QPushButton("编辑选中点")
        edit_btn.clicked.connect(self._edit_selected_point)
        control_layout.addWidget(edit_btn)

        delete_btn = QPushButton("删除选中点")
        delete_btn.clicked.connect(self._delete_selected_point)
        control_layout.addWidget(delete_btn)

        add_btn = QPushButton("添加点")
        add_btn.clicked.connect(self._add_point_dialog)
        control_layout.addWidget(add_btn)

        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)

        splitter.addWidget(left_widget)

        # 右侧: 数据表格
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        table_group = QGroupBox("数据表格")
        table_layout = QVBoxLayout()

        # 创建表格
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["索引", "X坐标", "Y坐标"])

        # 设置表格属性
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

        # 列宽
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        # 连接信号
        self.data_table.cellChanged.connect(self._on_table_cell_changed)
        self.data_table.itemSelectionChanged.connect(self._on_table_selection_changed)

        table_layout.addWidget(self.data_table)
        table_group.setLayout(table_layout)
        right_layout.addWidget(table_group)

        # 说明标签
        instruction_label = QLabel(
            "操作提示:\n"
            "• 鼠标滚轮缩放 | 左键拖动平移 | 单击选中点 | 双击编辑点 | 右键添加/删除点\n"
            "• 表格支持直接编辑 | Ctrl+C复制到Excel | Ctrl+A全选"
        )
        instruction_label.setStyleSheet("color: #666; font-size: 10px; padding: 10px;")
        right_layout.addWidget(instruction_label)

        splitter.addWidget(right_widget)

        # 设置分割比例
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setMinimumHeight(25)
        main_layout.addWidget(self.status_label)

    def set_processor(self, processor):
        """设置核心处理器"""
        self.processor = processor

    def set_callbacks(self, import_csv, generate_map, update_point, delete_point, add_point, save_csv):
        """设置回调函数"""
        self.on_import_csv = import_csv
        self.on_generate_map = generate_map
        self.on_update_point = update_point
        self.on_delete_point = delete_point
        self.on_add_point = add_point
        self.on_save_csv = save_csv

    def _import_csv(self):
        """导入CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*.*)"
        )

        if file_path and self.on_import_csv:
            success = self.on_import_csv(file_path)
            if success:
                self._refresh_display()
                self.status_label.setText(f"已导入: {file_path}")
            else:
                QMessageBox.critical(self, "错误", "导入CSV失败")

    def _new_map(self):
        """新建Map"""
        dialog = NewMapDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            params = dialog.get_parameters()
            if self.on_generate_map:
                success = self.on_generate_map(*params)
                if success:
                    self._refresh_display()
                    self.status_label.setText("已创建新Map")
                else:
                    QMessageBox.critical(self, "错误", "创建Map失败")

    def _save_csv(self):
        """保存CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存CSV文件", "", "CSV文件 (*.csv);;所有文件 (*.*)"
        )

        if file_path and self.on_save_csv:
            success = self.on_save_csv(file_path)
            if success:
                self.status_label.setText(f"已保存: {file_path}")
            else:
                QMessageBox.critical(self, "错误", "保存CSV失败")

    def _refresh_display(self):
        """刷新显示"""
        if not self.processor:
            return

        # 更新可视化
        points = self.processor.get_points()
        bounds = self.processor.get_boundaries()
        self.map_view.set_points(points, bounds['center_x'], bounds['center_y'])

        # 更新表格
        self._update_table()

        # 更新状态
        stats = self.processor.get_statistics()
        self.status_label.setText(
            f"总点数: {stats['total_points']} | "
            f"X范围: ({stats['x_range'][0]:.2f}, {stats['x_range'][1]:.2f}) | "
            f"Y范围: ({stats['y_range'][0]:.2f}, {stats['y_range'][1]:.2f})"
        )

    def _update_table(self):
        """更新表格数据"""
        if not self.processor:
            return

        points = self.processor.get_points()

        # 阻止信号,避免触发cellChanged
        self.data_table.blockSignals(True)
        self.data_table.setRowCount(0)

        for i, (x, y) in enumerate(points):
            self.data_table.insertRow(i)

            # 索引
            item_idx = QTableWidgetItem(str(i))
            item_idx.setFlags(item_idx.flags() & ~Qt.ItemIsEditable)
            item_idx.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(i, 0, item_idx)

            # X坐标
            item_x = QTableWidgetItem(f"{x:.6f}".rstrip('0').rstrip('.'))
            item_x.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(i, 1, item_x)

            # Y坐标
            item_y = QTableWidgetItem(f"{y:.6f}".rstrip('0').rstrip('.'))
            item_y.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(i, 2, item_y)

        self.data_table.blockSignals(False)

    def _on_point_selected(self, data):
        """点选中回调"""
        if isinstance(data, int):
            # 单纯选中
            self._sync_table_selection(data)
        elif isinstance(data, tuple):
            # 操作
            op = data[0]
            if op == -1:  # 添加
                x, y = data[1], data[2]
                if self.on_add_point:
                    self.on_add_point(x, y)
                    self._refresh_display()
            elif op == -2:  # 删除
                idx = self.map_view.get_selected_index()
                if idx is not None and self.on_delete_point:
                    self.on_delete_point(idx)
                    self._refresh_display()

    def _on_point_double_clicked(self, index: int):
        """双击点编辑"""
        self._edit_point_at(index)

    def _edit_selected_point(self):
        """编辑选中的点"""
        idx = self.map_view.get_selected_index()
        if idx is not None:
            self._edit_point_at(idx)
        else:
            QMessageBox.warning(self, "提示", "请先在可视化图中选择一个点")

    def _edit_point_at(self, index: int):
        """编辑指定索引的点"""
        if not self.processor or index < 0 or index >= len(self.processor.get_points()):
            return

        points = self.processor.get_points()
        current_x, current_y = points[index]

        # 弹出对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑点 [{index}]")
        layout = QFormLayout()

        x_spin = QDoubleSpinBox()
        x_spin.setRange(-1000, 1000)
        x_spin.setValue(current_x)
        x_spin.setDecimals(4)
        layout.addRow("X坐标:", x_spin)

        y_spin = QDoubleSpinBox()
        y_spin.setRange(-1000, 1000)
        y_spin.setValue(current_y)
        y_spin.setDecimals(4)
        layout.addRow("Y坐标:", y_spin)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            new_x = x_spin.value()
            new_y = y_spin.value()

            if self.on_update_point:
                success = self.on_update_point(index, new_x, new_y)
                if success:
                    self._refresh_display()
                else:
                    QMessageBox.critical(self, "错误", "更新点失败")

    def _delete_selected_point(self):
        """删除选中的点"""
        idx = self.map_view.get_selected_index()
        if idx is not None:
            if self.on_delete_point:
                self.on_delete_point(idx)
                self._refresh_display()
        else:
            QMessageBox.warning(self, "提示", "请先在可视化图中选择一个点")

    def _add_point_dialog(self):
        """添加点对话框"""
        if not self.processor:
            return

        bounds = self.processor.get_boundaries()

        dialog = QDialog(self)
        dialog.setWindowTitle("添加点")
        layout = QFormLayout()

        x_spin = QDoubleSpinBox()
        x_spin.setRange(-1000, 1000)
        x_spin.setValue(bounds['center_x'])
        x_spin.setDecimals(4)
        layout.addRow("X坐标:", x_spin)

        y_spin = QDoubleSpinBox()
        y_spin.setRange(-1000, 1000)
        y_spin.setValue(bounds['center_y'])
        y_spin.setDecimals(4)
        layout.addRow("Y坐标:", y_spin)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            x = x_spin.value()
            y = y_spin.value()

            if self.on_add_point:
                self.on_add_point(x, y)
                self._refresh_display()

    def _on_table_cell_changed(self, row: int, col: int):
        """表格单元格改变"""
        if not self.processor:
            return

        if col not in [1, 2]:  # 只处理X和Y列
            return

        try:
            item = self.data_table.item(row, col)
            if item is None:
                return

            value = float(item.text())

            # 获取当前行的完整数据
            x_item = self.data_table.item(row, 1)
            y_item = self.data_table.item(row, 2)

            if x_item is None or y_item is None:
                return

            x = float(x_item.text()) if col != 1 else value
            y = float(y_item.text()) if col != 2 else value

            if self.on_update_point:
                self.on_update_point(row, x, y)
                self._refresh_display()

        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
            self._update_table()  # 恢复原值

    def _on_table_selection_changed(self):
        """表格选择改变"""
        selected_items = self.data_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.map_view.set_selected_index(row)
        else:
            self.map_view.set_selected_index(None)

    def _sync_table_selection(self, index: Optional[int]):
        """同步表格选择"""
        if index is None:
            self.data_table.clearSelection()
        else:
            self.data_table.selectRow(index)

    def keyPressEvent(self, event):
        """键盘事件"""
        # Ctrl+C 复制
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self._copy_selection_to_clipboard()
            return

        # Ctrl+A 全选
        if event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            self.data_table.selectAll()
            return

        super().keyPressEvent(event)

    def _copy_selection_to_clipboard(self):
        """复制选中内容到剪贴板"""
        clipboard = QApplication.clipboard()
        selected_items = self.data_table.selectedItems()

        if not selected_items:
            return

        # 获取选中的行
        selected_rows = set(item.row() for item in selected_items)

        # 构建文本
        text_lines = []

        # 表头
        text_lines.append("索引\tX坐标\tY坐标")

        # 数据行
        for row in sorted(selected_rows):
            idx_item = self.data_table.item(row, 0)
            x_item = self.data_table.item(row, 1)
            y_item = self.data_table.item(row, 2)

            if idx_item and x_item and y_item:
                text_lines.append(f"{idx_item.text()}\t{x_item.text()}\t{y_item.text()}")

        # 设置到剪贴板
        clipboard.setText("\n".join(text_lines))
        self.status_label.setText(f"已复制 {len(selected_rows)} 行数据到剪贴板")
