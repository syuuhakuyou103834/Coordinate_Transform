"""
Map建立UI界面模块 - PyQt5版本
负责创建图形用户界面和用户交互，支持Map预览和生成
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QRadioButton, QButtonGroup, QGroupBox, QFileDialog,
    QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPolygon
from typing import Optional, Callable, List, Tuple
import os
import sys


class MapPreviewWidget(QWidget):
    """Map预览控件 - 显示点和扫描路径"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = []  # 点列表
        self.path_lines = []  # 路径线段
        self.radius = 100.0  # 圆半径
        self.setMinimumSize(400, 400)
        self.setStyleSheet("background-color: white; border: 1px solid #ccc;")

    def set_data(self, scan_path: List[Tuple[float, float]], radius: float):
        """
        设置要显示的数据

        Args:
            scan_path: 扫描路径点列表
            radius: 圆半径
        """
        self.points = scan_path
        self.radius = radius
        self.path_lines = scan_path  # 路径就是点的顺序
        self.update()

    def clear_data(self):
        """清空数据"""
        self.points = []
        self.path_lines = []
        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取控件尺寸
        width = self.width()
        height = self.height()

        # 计算缩放比例（留出边距）
        margin = 40
        draw_width = width - 2 * margin
        draw_height = height - 2 * margin

        # 计算缩放比例（确保圆完整显示）
        scale = min(draw_width, draw_height) / (2 * self.radius * 1.1)

        # 计算中心点
        center_x = width / 2
        center_y = height / 2

        # 绘制晶圆圆形边界
        circle_radius = self.radius * scale
        painter.setPen(QPen(QColor("#333"), 2))
        painter.setBrush(QBrush(QColor("#f0f0f0")))
        painter.drawEllipse(QPoint(int(center_x), int(center_y)),
                          int(circle_radius), int(circle_radius))

        # 绘制坐标轴
        painter.setPen(QPen(QColor("#999"), 1, Qt.DashLine))
        # X轴
        painter.drawLine(int(center_x - circle_radius - 10), int(center_y),
                        int(center_x + circle_radius + 10), int(center_y))
        # Y轴
        painter.drawLine(int(center_x), int(center_y - circle_radius - 10),
                        int(center_x), int(center_y + circle_radius + 10))

        # 绘制扫描路径线
        if len(self.path_lines) > 1:
            painter.setPen(QPen(QColor("#6699CC"), 1, Qt.SolidLine))
            for i in range(len(self.path_lines) - 1):
                x1, y1 = self.path_lines[i]
                x2, y2 = self.path_lines[i + 1]

                # 转换坐标
                px1 = center_x + x1 * scale
                py1 = center_y - y1 * scale  # Y轴反转
                px2 = center_x + x2 * scale
                py2 = center_y - y2 * scale

                painter.drawLine(int(px1), int(py1), int(px2), int(py2))

        # 绘制点
        if self.points:
            painter.setPen(QPen(QColor("#0066CC"), 1))
            painter.setBrush(QBrush(QColor("#0066CC")))

            for i, (x, y) in enumerate(self.points):
                # 转换坐标
                px = center_x + x * scale
                py = center_y - y * scale  # Y轴反转

                # 起点用不同颜色
                if i == 0:
                    painter.setPen(QPen(QColor("#FF0000"), 2))
                    painter.setBrush(QBrush(QColor("#FF0000")))
                    radius = 5
                elif i == len(self.points) - 1:
                    painter.setPen(QPen(QColor("#00CC00"), 2))
                    painter.setBrush(QBrush(QColor("#00CC00")))
                    radius = 5
                else:
                    painter.setPen(QPen(QColor("#0066CC"), 1))
                    painter.setBrush(QBrush(QColor("#0066CC")))
                    radius = 3

                painter.drawEllipse(QPoint(int(px), int(py)), radius, radius)

        # 绘制比例尺
        self._draw_scale(painter, width, height, margin, scale)

        # 绘制统计信息
        if self.points:
            self._draw_statistics(painter, width, height, margin)

    def _draw_scale(self, painter: QPainter, width: int, height: int, margin: int, scale: float):
        """绘制比例尺"""
        scale_length = 50  # 50mm
        scale_pixels = scale_length * scale

        # 在右下角绘制比例尺
        x = width - margin - scale_pixels - 20
        y = height - margin - 20

        painter.setPen(QPen(QColor("#333"), 2))
        painter.drawLine(int(x), int(y), int(x + scale_pixels), int(y))
        painter.drawLine(int(x), int(y - 5), int(x), int(y + 5))
        painter.drawLine(int(x + scale_pixels), int(y - 5), int(x + scale_pixels), int(y + 5))

        painter.setPen(QColor("#333"))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(int(x + scale_pixels / 2 - 15), int(y - 8), f"{scale_length}mm")

    def _draw_statistics(self, painter: QPainter, width: int, height: int, margin: int):
        """绘制统计信息"""
        text = f"总点数: {len(self.points)}"
        painter.setPen(QColor("#333"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(margin + 10, margin + 20, text)


class MapEstablishUI(QMainWindow):
    """Map建立UI界面 - PyQt5版本"""

    def __init__(self):
        super().__init__()
        self.on_preview = None
        self.on_generate = None
        self.current_scan_path = []
        self.current_stats = {}

        self._setup_ui()

    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("Map建立工具")
        self.setMinimumSize(900, 700)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== 左侧控制面板 =====
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(10)

        # 1. 晶圆尺寸选择
        wafer_group = QGroupBox("晶圆尺寸")
        wafer_layout = QVBoxLayout()

        self.wafer_radio_group = QButtonGroup(self)
        self.wafer_4 = QRadioButton("4 inch (直径100mm)")
        self.wafer_6 = QRadioButton("6 inch (直径150mm)")
        self.wafer_8 = QRadioButton("8 inch (直径200mm)")

        self.wafer_8.setChecked(True)  # 默认选中8 inch

        self.wafer_radio_group.addButton(self.wafer_4)
        self.wafer_radio_group.addButton(self.wafer_6)
        self.wafer_radio_group.addButton(self.wafer_8)

        wafer_layout.addWidget(self.wafer_4)
        wafer_layout.addWidget(self.wafer_6)
        wafer_layout.addWidget(self.wafer_8)
        wafer_group.setLayout(wafer_layout)

        control_layout.addWidget(wafer_group)

        # 2. 参考点坐标
        ref_group = QGroupBox("参考点坐标 (mm)")
        ref_layout = QGridLayout()

        ref_layout.addWidget(QLabel("X坐标:"), 0, 0)
        self.ref_x_edit = QLineEdit("0")
        self.ref_x_edit.setPlaceholderText("例如: 0")
        ref_layout.addWidget(self.ref_x_edit, 0, 1)

        ref_layout.addWidget(QLabel("Y坐标:"), 1, 0)
        self.ref_y_edit = QLineEdit("0")
        self.ref_y_edit.setPlaceholderText("例如: 0")
        ref_layout.addWidget(self.ref_y_edit, 1, 1)

        ref_group.setLayout(ref_layout)
        control_layout.addWidget(ref_group)

        # 3. 点间距
        pitch_group = QGroupBox("点间距 (mm)")
        pitch_layout = QGridLayout()

        pitch_layout.addWidget(QLabel("X Pitch:"), 0, 0)
        self.x_pitch_edit = QLineEdit("2.00")
        self.x_pitch_edit.setPlaceholderText("例如: 2.00")
        pitch_layout.addWidget(self.x_pitch_edit, 0, 1)

        pitch_layout.addWidget(QLabel("Y Pitch:"), 1, 0)
        self.y_pitch_edit = QLineEdit("2.00")
        self.y_pitch_edit.setPlaceholderText("例如: 2.00")
        pitch_layout.addWidget(self.y_pitch_edit, 1, 1)

        pitch_group.setLayout(pitch_layout)
        control_layout.addWidget(pitch_group)

        # 4. 起点位置
        start_group = QGroupBox("起点位置")
        start_layout = QGridLayout()

        self.start_radio_group = QButtonGroup(self)
        self.start_tl = QRadioButton("左上 (X_min, Y_max)")
        self.start_tr = QRadioButton("右上 (X_max, Y_max)")
        self.start_bl = QRadioButton("左下 (X_min, Y_min)")
        self.start_br = QRadioButton("右下 (X_max, Y_min)")

        self.start_bl.setChecked(True)  # 默认左下

        self.start_radio_group.addButton(self.start_tl)
        self.start_radio_group.addButton(self.start_tr)
        self.start_radio_group.addButton(self.start_bl)
        self.start_radio_group.addButton(self.start_br)

        start_layout.addWidget(self.start_tl, 0, 0)
        start_layout.addWidget(self.start_tr, 0, 1)
        start_layout.addWidget(self.start_bl, 1, 0)
        start_layout.addWidget(self.start_br, 1, 1)

        start_group.setLayout(start_layout)
        control_layout.addWidget(start_group)

        # 5. 行进方向
        direction_group = QGroupBox("行进方向")
        direction_layout = QHBoxLayout()

        self.direction_radio_group = QButtonGroup(self)
        self.direction_x = QRadioButton("X方向 (蛇形扫描)")
        self.direction_y = QRadioButton("Y方向 (蛇形扫描)")

        self.direction_x.setChecked(True)  # 默认X方向

        self.direction_radio_group.addButton(self.direction_x)
        self.direction_radio_group.addButton(self.direction_y)

        direction_layout.addWidget(self.direction_x)
        direction_layout.addWidget(self.direction_y)
        direction_group.setLayout(direction_layout)

        control_layout.addWidget(direction_group)

        # 6. 按钮区域
        button_layout = QHBoxLayout()

        self.preview_btn = QPushButton("预览")
        self.preview_btn.setMinimumHeight(40)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #0088CC;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0099DD;
            }
            QPushButton:pressed {
                background-color: #0077BB;
            }
        """)
        self.preview_btn.clicked.connect(self._preview_map)

        self.generate_btn = QPushButton("生成CSV")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00CC66;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00DD77;
            }
            QPushButton:pressed {
                background-color: #00BB55;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.generate_btn.clicked.connect(self._generate_csv)

        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.generate_btn)
        control_layout.addLayout(button_layout)

        # 7. 统计信息
        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("请先点击预览按钮")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("color: #666; font-size: 11px;")

        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)

        control_layout.addWidget(stats_group)

        # 添加弹性空间
        control_layout.addStretch()

        control_widget.setMaximumWidth(350)
        main_layout.addWidget(control_widget)

        # ===== 右侧预览区域 =====
        preview_group = QGroupBox("Map预览")
        preview_layout = QVBoxLayout()

        self.preview_widget = MapPreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        # 说明文字
        instruction_label = QLabel(
            "红色点: 起点 | 蓝色点: 测量点 | 绿色点: 终点\n"
            "蓝色线条: 扫描路径"
        )
        instruction_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        instruction_label.setAlignment(Qt.AlignCenter)

        preview_layout.addWidget(instruction_label)
        preview_group.setLayout(preview_layout)

        main_layout.addWidget(preview_group, 1)  # stretch factor = 1

        # ===== 状态栏 =====
        self.status_label = QLabel("就绪")
        self.status_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status_label.setMinimumHeight(25)

        main_layout.addWidget(self.status_label)

    def _get_wafer_size(self) -> str:
        """获取选中的晶圆尺寸"""
        if self.wafer_4.isChecked():
            return "4 inch"
        elif self.wafer_6.isChecked():
            return "6 inch"
        else:
            return "8 inch"

    def _get_start_position(self) -> str:
        """获取选中的起点位置"""
        if self.start_tl.isChecked():
            return "左上"
        elif self.start_tr.isChecked():
            return "右上"
        elif self.start_bl.isChecked():
            return "左下"
        else:
            return "右下"

    def _get_scan_direction(self) -> str:
        """获取选中的扫描方向"""
        if self.direction_x.isChecked():
            return "X方向"
        else:
            return "Y方向"

    def _preview_map(self):
        """预览Map"""
        print("\n" + "="*60)
        print("[UI] 点击预览按钮")
        print("="*60)

        try:
            # 获取原始输入文本
            ref_x_text = self.ref_x_edit.text().strip()
            ref_y_text = self.ref_y_edit.text().strip()
            x_pitch_text = self.x_pitch_edit.text().strip()
            y_pitch_text = self.y_pitch_edit.text().strip()

            # 记录原始输入
            print(f"[UI] 原始输入 - ref_x_text: '{ref_x_text}' (type: {type(ref_x_text).__name__})")
            print(f"[UI] 原始输入 - ref_y_text: '{ref_y_text}' (type: {type(ref_y_text).__name__})")
            print(f"[UI] 原始输入 - x_pitch_text: '{x_pitch_text}' (type: {type(x_pitch_text).__name__})")
            print(f"[UI] 原始输入 - y_pitch_text: '{y_pitch_text}' (type: {type(y_pitch_text).__name__})")

            # 检查是否为空输入
            if ref_x_text == "" or ref_y_text == "":
                print("[UI] 错误：参考点坐标为空")
                QMessageBox.warning(self, "警告", "请输入参考点坐标")
                self.status_label.setText("参数错误：缺少参考点坐标")
                return

            if x_pitch_text == "" or y_pitch_text == "":
                print("[UI] 错误：点间距为空")
                QMessageBox.warning(self, "警告", "请输入点间距")
                self.status_label.setText("参数错误：缺少点间距")
                return

            # 转换为数字（添加详细日志）
            print("[UI] 开始转换输入值为数字...")
            wafer_size = self._get_wafer_size()
            print(f"[UI] 晶圆尺寸: {wafer_size}")

            try:
                ref_x = float(ref_x_text)
                print(f"[UI] 转换成功 - ref_x: {ref_x}")
            except ValueError as e:
                print(f"[UI] 转换失败 - ref_x_text: '{ref_x_text}', 错误: {e}")
                raise

            try:
                ref_y = float(ref_y_text)
                print(f"[UI] 转换成功 - ref_y: {ref_y}")
            except ValueError as e:
                print(f"[UI] 转换失败 - ref_y_text: '{ref_y_text}', 错误: {e}")
                raise

            try:
                x_pitch = float(x_pitch_text)
                print(f"[UI] 转换成功 - x_pitch: {x_pitch}")
            except ValueError as e:
                print(f"[UI] 转换失败 - x_pitch_text: '{x_pitch_text}', 错误: {e}")
                raise

            try:
                y_pitch = float(y_pitch_text)
                print(f"[UI] 转换成功 - y_pitch: {y_pitch}")
            except ValueError as e:
                print(f"[UI] 转换失败 - y_pitch_text: '{y_pitch_text}', 错误: {e}")
                raise

            start_position = self._get_start_position()
            scan_direction = self._get_scan_direction()
            print(f"[UI] 起点位置: {start_position}")
            print(f"[UI] 扫描方向: {scan_direction}")

            # 验证数值范围
            if x_pitch <= 0 or y_pitch <= 0:
                print(f"[UI] 错误：间距必须大于0 (x_pitch={x_pitch}, y_pitch={y_pitch})")
                QMessageBox.warning(self, "警告", "点间距必须大于0")
                self.status_label.setText("参数错误：间距必须大于0")
                return

            print("[UI] 参数验证通过，调用核心处理模块...")
            # 调用预览回调
            if self.on_preview:
                scan_path, stats = self.on_preview(
                    wafer_size, ref_x, ref_y, x_pitch, y_pitch,
                    start_position, scan_direction
                )

                print(f"[UI] 核心处理返回 - 总点数: {stats['total_points']}")
                self.current_scan_path = scan_path
                self.current_stats = stats

                # 更新预览
                self.preview_widget.set_data(scan_path, stats['radius'])

                # 更新统计信息
                bounds = stats['boundaries']
                stats_text = f"""
总点数: {stats['total_points']}
晶圆尺寸: {stats['wafer_size']} (半径: {stats['radius']:.1f}mm)
X间距: {stats['x_pitch']:.2f}mm
Y间距: {stats['y_pitch']:.2f}mm
起点位置: {start_position}
行进方向: {scan_direction}

边界范围:
X: {bounds['x_min']:.2f} ~ {bounds['x_max']:.2f} mm
Y: {bounds['y_min']:.2f} ~ {bounds['y_max']:.2f} mm
                """.strip()
                self.stats_label.setText(stats_text)

                # 启用生成按钮
                self.generate_btn.setEnabled(True)

                self.status_label.setText(f"预览完成 - 共 {stats['total_points']} 个点")
                print(f"[UI] 预览完成！")

        except ValueError as e:
            print(f"[UI] ValueError异常: {e}")
            print(f"[UI] 异常类型: {type(e).__name__}")
            import traceback
            print(f"[UI] 完整堆栈:\n{traceback.format_exc()}")
            QMessageBox.critical(self, "错误", "请输入有效的数字")
            self.status_label.setText("参数错误：无效的数字格式")
        except Exception as e:
            print(f"[UI] 未知异常: {e}")
            print(f"[UI] 异常类型: {type(e).__name__}")
            import traceback
            print(f"[UI] 完整堆栈:\n{traceback.format_exc()}")
            QMessageBox.critical(self, "错误", f"预览失败：{str(e)}")
            self.status_label.setText(f"预览失败：{str(e)}")

    def _generate_csv(self):
        """生成CSV文件"""
        if not self.current_scan_path:
            QMessageBox.warning(self, "警告", "请先预览Map")
            return

        try:
            # 弹出文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存Map文件",
                "",
                "CSV文件 (*.csv);;所有文件 (*.*)"
            )

            if file_path:
                # 获取pitch字符串（用于确定精度）
                x_pitch_str = self.x_pitch_edit.text().strip()
                y_pitch_str = self.y_pitch_edit.text().strip()

                if self.on_generate:
                    success = self.on_generate(self.current_scan_path, file_path, x_pitch_str, y_pitch_str)

                    if success:
                        self.status_label.setText(f"已保存: {os.path.basename(file_path)}")
                        QMessageBox.information(self, "成功",
                                             f"Map文件已成功保存！\n"
                                             f"文件路径: {file_path}\n"
                                             f"总点数: {len(self.current_scan_path)}")
                    else:
                        QMessageBox.critical(self, "错误", "保存CSV文件失败")
                        self.status_label.setText("保存失败")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成CSV时出错：{str(e)}")
            self.status_label.setText("生成失败")

    def set_callbacks(self, preview: Callable, generate: Callable):
        """设置回调函数"""
        self.on_preview = preview
        self.on_generate = generate
