"""
UI界面模块 - PyQt5版本
负责创建图形用户界面和用户交互，支持表格数据复制到Excel
"""

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QGroupBox, QTextEdit, QFrame, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize, QItemSelectionModel
from PyQt5.QtGui import QFont, QColor, QKeySequence
from typing import Optional, Callable
import os


class MapDataUI(QMainWindow):
    """地图数据处理UI界面 - PyQt5版本"""

    def __init__(self):
        super().__init__()
        self.on_load_file = None
        self.on_search_x = None
        self.on_search_y = None
        self.current_file_path = None

        # 用于跟踪最后点击的单元格，实现Shift连续选择
        self.last_clicked_item = None

        self._setup_ui()

    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("地图坐标查询系统")
        self.setMinimumSize(1200, 700)

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== 文件选择区域 =====
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout()

        file_label = QLabel("CSV文件:")
        file_label.setMinimumWidth(70)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("请选择CSV文件...")

        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setMinimumWidth(100)
        self.browse_btn.clicked.connect(self._browse_file)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_btn)
        file_group.setLayout(file_layout)

        main_layout.addWidget(file_group)

        # 创建中间的水平布局（左侧控制，右侧结果）
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)

        # ===== 查询控制区域 =====
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(10)

        # X坐标查询组
        x_group = QGroupBox("X坐标查询")
        x_layout = QVBoxLayout()

        x_input_layout = QHBoxLayout()
        x_label = QLabel("输入X值:")
        x_label.setMinimumWidth(70)
        self.x_value_edit = QLineEdit()
        self.x_value_edit.setPlaceholderText("输入X坐标值...")
        x_input_layout.addWidget(x_label)
        x_input_layout.addWidget(self.x_value_edit)

        self.search_x_btn = QPushButton("查询X坐标")
        self.search_x_btn.setEnabled(False)
        self.search_x_btn.setMinimumHeight(35)
        self.search_x_btn.clicked.connect(self._search_x)

        x_layout.addLayout(x_input_layout)
        x_layout.addWidget(self.search_x_btn)
        x_group.setLayout(x_layout)

        control_layout.addWidget(x_group)

        # Y坐标查询组
        y_group = QGroupBox("Y坐标查询")
        y_layout = QVBoxLayout()

        y_input_layout = QHBoxLayout()
        y_label = QLabel("输入Y值:")
        y_label.setMinimumWidth(70)
        self.y_value_edit = QLineEdit()
        self.y_value_edit.setPlaceholderText("输入Y坐标值...")
        y_input_layout.addWidget(y_label)
        y_input_layout.addWidget(self.y_value_edit)

        self.search_y_btn = QPushButton("查询Y坐标")
        self.search_y_btn.setEnabled(False)
        self.search_y_btn.setMinimumHeight(35)
        self.search_y_btn.clicked.connect(self._search_y)

        y_layout.addLayout(y_input_layout)
        y_layout.addWidget(self.search_y_btn)
        y_group.setLayout(y_layout)

        control_layout.addWidget(y_group)

        # 数据摘要组
        summary_group = QGroupBox("数据摘要")
        summary_layout = QVBoxLayout()

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(200)
        self.summary_text.setMaximumHeight(200)
        self.summary_text.setPlaceholderText("加载数据后显示摘要信息...")

        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)

        control_layout.addWidget(summary_group)

        # 添加弹性空间
        control_layout.addStretch()

        control_widget.setMaximumWidth(350)
        middle_layout.addWidget(control_widget)

        # ===== 结果显示区域 =====
        result_group = QGroupBox("查询结果")
        result_layout = QVBoxLayout()

        # 创建表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["X坐标", "Y坐标", "膜厚"])

        # 设置表格属性 - 修改为支持多选
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectItems)  # 选择单元格而非整行
        self.result_table.setSelectionMode(QAbstractItemView.ExtendedSelection)  # 支持扩展选择（Ctrl多选）
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 连接点击事件，用于实现Shift连续选择
        self.result_table.itemClicked.connect(self._on_item_clicked)

        # 设置列宽
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        # 设置表格样式
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f0f0f0;
                background-color: white;
                gridline-color: #d0d0d0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)

        # 添加说明标签
        instruction_label = QLabel(
            "提示：支持Excel式选择 - 单击选中 | Ctrl+点击多选 | Shift+点击连续选择 | Ctrl+A全选 | Ctrl+C复制"
        )
        instruction_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")

        result_layout.addWidget(self.result_table)
        result_layout.addWidget(instruction_label)
        result_group.setLayout(result_layout)

        middle_layout.addWidget(result_group, 1)  # stretch factor = 1

        main_layout.addLayout(middle_layout, 1)  # stretch factor = 1

        # ===== 状态栏 =====
        self.status_label = QLabel("请加载CSV文件")
        self.status_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status_label.setMinimumHeight(25)

        main_layout.addWidget(self.status_label)

    def _browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择CSV文件",
            "",
            "CSV文件 (*.csv);;所有文件 (*.*)"
        )

        if file_path:
            self.current_file_path = file_path
            self.file_path_edit.setText(file_path)
            self._load_file()

    def _load_file(self):
        """加载文件"""
        if self.on_load_file and self.current_file_path:
            success = self.on_load_file(self.current_file_path)
            if success:
                self.search_x_btn.setEnabled(True)
                self.search_y_btn.setEnabled(True)
                self.status_label.setText(f"已加载: {os.path.basename(self.current_file_path)}")
            else:
                QMessageBox.critical(self, "错误", "加载CSV文件失败")
                self.status_label.setText("加载失败")

    def _search_x(self):
        """查询X坐标"""
        x_str = self.x_value_edit.text().strip()
        if not x_str:
            QMessageBox.warning(self, "警告", "请输入X坐标值")
            return

        try:
            x_value = float(x_str)
            if self.on_search_x:
                results = self.on_search_x(x_value)
                self._display_results(results, f"X坐标 = {x_value}")
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的数字")

    def _search_y(self):
        """查询Y坐标"""
        y_str = self.y_value_edit.text().strip()
        if not y_str:
            QMessageBox.warning(self, "警告", "请输入Y坐标值")
            return

        try:
            y_value = float(y_str)
            if self.on_search_y:
                results = self.on_search_y(y_value)
                self._display_results(results, f"Y坐标 = {y_value}")
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的数字")

    def _display_results(self, results: list, title: str):
        """显示查询结果"""
        # 清空现有结果
        self.result_table.setRowCount(0)
        # 重置最后点击的单元格
        self.last_clicked_item = None

        if not results:
            self.status_label.setText(f"{title} - 未找到匹配结果")
            QMessageBox.information(self, "查询结果", f"{title}\n未找到匹配的数据点")
            return

        # 添加新结果
        self.result_table.setRowCount(len(results))
        for row, (x, y, thickness) in enumerate(results):
            # X坐标
            item_x = QTableWidgetItem(f"{x:.6f}".rstrip('0').rstrip('.') if isinstance(x, float) else str(x))
            item_x.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 0, item_x)

            # Y坐标
            item_y = QTableWidgetItem(f"{y:.6f}".rstrip('0').rstrip('.') if isinstance(y, float) else str(y))
            item_y.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 1, item_y)

            # 膜厚
            item_t = QTableWidgetItem(f"{thickness:.5f}".rstrip('0').rstrip('.') if isinstance(thickness, float) else str(thickness))
            item_t.setTextAlignment(Qt.AlignCenter)
            self.result_table.setItem(row, 2, item_t)

        self.status_label.setText(f"{title} - 找到 {len(results)} 条结果")

    def set_data_summary(self, summary: str):
        """设置数据摘要信息"""
        self.summary_text.setPlainText(summary)

    def clear_results(self):
        """清空结果表格"""
        self.result_table.setRowCount(0)

    def set_callbacks(self, load_file: Callable, search_x: Callable, search_y: Callable):
        """设置回调函数"""
        self.on_load_file = load_file
        self.on_search_x = search_x
        self.on_search_y = search_y

    def keyPressEvent(self, event):
        """处理键盘事件 - 实现复制和全选功能"""
        # Ctrl+A 全选
        if event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            if self.result_table.hasFocus():
                self.result_table.selectAll()
                return

        # Ctrl+C 复制
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            if self.result_table.hasFocus():
                self._copy_selection_to_clipboard()
                return

        super().keyPressEvent(event)

    def _on_item_clicked(self, item):
        """处理单元格点击事件，实现Shift连续选择"""
        modifiers = QApplication.keyboardModifiers()

        # Shift键：从上次点击的位置到当前位置连续选择
        if modifiers == Qt.ShiftModifier and self.last_clicked_item is not None:
            last_row = self.last_clicked_item.row()
            last_col = self.last_clicked_item.column()
            current_row = item.row()
            current_col = item.column()

            # 清除现有选择
            self.result_table.clearSelection()

            # 确定选择范围的边界
            start_row = min(last_row, current_row)
            end_row = max(last_row, current_row)
            start_col = min(last_col, current_col)
            end_col = max(last_col, current_col)

            # 选中范围内的所有单元格
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    if self.result_table.item(row, col):
                        self.result_table.item(row, col).setSelected(True)

        # 更新最后点击的单元格
        self.last_clicked_item = item

    def _copy_selection_to_clipboard(self):
        """复制选中内容到剪贴板（制表符分隔，可直接粘贴到Excel）"""
        clipboard = QApplication.clipboard()
        selected_items = self.result_table.selectedItems()

        if not selected_items:
            return

        # 获取选中单元格的行列范围
        selected_rows = set()
        selected_cols = set()
        for item in selected_items:
            selected_rows.add(item.row())
            selected_cols.add(item.column())

        if not selected_rows:
            return

        # 构建复制文本（制表符分隔）
        text_lines = []

        # 添加表头
        min_col = min(selected_cols)
        max_col = max(selected_cols)
        headers = []
        for col in range(min_col, max_col + 1):
            headers.append(self.result_table.horizontalHeaderItem(col).text())
        text_lines.append("\t".join(headers))

        # 添加数据行
        min_row = min(selected_rows)
        max_row = max(selected_rows)

        for row in range(min_row, max_row + 1):
            row_data = []
            for col in range(min_col, max_col + 1):
                item = self.result_table.item(row, col)
                if item and item.isSelected():
                    row_data.append(item.text())
                else:
                    row_data.append("")
            text_lines.append("\t".join(row_data))

        # 设置到剪贴板
        clipboard.setText("\n".join(text_lines))
        self.status_label.setText(f"已复制 {len(selected_rows)} 行 x {len(selected_cols)} 列数据到剪贴板")
