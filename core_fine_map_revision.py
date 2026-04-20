"""
Fine Map Revision 核心功能模块
负责Map数据的生成、导入、编辑和导出
"""

import pandas as pd
from typing import List, Tuple, Dict, Optional
import math

# 调试标志
DEBUG_MODE = True

def debug_print(msg: str):
    """调试输出函数"""
    if DEBUG_MODE:
        print(f"[FineMap Core] {msg}")


class FineMapRevisionProcessor:
    """精细Map修订处理器"""

    def __init__(self):
        debug_print("=" * 60)
        debug_print("FineMapRevisionProcessor 初始化")
        self.points = []  # 存储点坐标列表 [(x, y), ...]
        self.center_x = 0.0
        self.center_y = 0.0
        self.x_min = 0.0
        self.x_max = 0.0
        self.y_min = 0.0
        self.y_max = 0.0
        self.x_pitch = 1.0
        self.y_pitch = 1.0
        debug_print("初始化完成")

    def load_from_csv(self, file_path: str) -> bool:
        """
        从CSV文件加载Map数据

        Args:
            file_path: CSV文件路径

        Returns:
            bool: 成功返回True
        """
        debug_print("\n" + "=" * 60)
        debug_print(f"load_from_csv() 开始执行")
        debug_print(f"参数: file_path = '{file_path}'")

        try:
            df = pd.read_csv(file_path)
            debug_print(f"CSV读取成功, 共 {len(df)} 行数据")

            # 检查列名
            if 'X' in df.columns and 'Y' in df.columns:
                x_col = 'X'
                y_col = 'Y'
                debug_print(f"检测到标准列名: {x_col}, {y_col}")
            elif 'x' in df.columns and 'y' in df.columns:
                x_col = 'x'
                y_col = 'y'
                debug_print(f"检测到小写列名: {x_col}, {y_col}")
            elif len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]
                debug_print(f"使用前两列作为坐标: {x_col}, {y_col}")
            else:
                debug_print("错误: CSV文件列数不足")
                return False

            # 读取数据
            self.points = []
            for idx, row in df.iterrows():
                x = float(row[x_col])
                y = float(row[y_col])
                self.points.append((x, y))

                if DEBUG_MODE and idx < 3:  # 只打印前3个点
                    debug_print(f"  读取点 {idx}: ({x:.4f}, {y:.4f})")

            # 计算边界和中心
            self._calculate_boundaries()

            debug_print(f"✓ load_from_csv() 成功完成")
            debug_print(f"  总点数: {len(self.points)}")
            debug_print(f"  X范围: [{self.x_min:.4f}, {self.x_max:.4f}]")
            debug_print(f"  Y范围: [{self.y_min:.4f}, {self.y_max:.4f}]")
            debug_print(f"  中心点: ({self.center_x:.4f}, {self.center_y:.4f})")
            return True
        except Exception as e:
            debug_print(f"✗ load_from_csv() 执行失败: {e}")
            return False

    def generate_rectangular_map(self, x_length: float, y_length: float,
                                 x_pitch: float, y_pitch: float,
                                 center_x: float, center_y: float) -> bool:
        """
        生成矩形Map点阵(以中心点为基准)

        Args:
            x_length: X方向长度 (x_Max - x_Min)
            y_length: Y方向长度 (y_Max - y_Min)
            x_pitch: X方向间距
            y_pitch: Y方向间距
            center_x: 中心点X坐标
            center_y: 中心点Y坐标

        Returns:
            bool: 成功返回True
        """
        debug_print("\n" + "=" * 60)
        debug_print(f"generate_rectangular_map() 开始执行")
        debug_print(f"输入参数:")
        debug_print(f"  x_length = {x_length:.4f}")
        debug_print(f"  y_length = {y_length:.4f}")
        debug_print(f"  x_pitch = {x_pitch:.4f}")
        debug_print(f"  y_pitch = {y_pitch:.4f}")
        debug_print(f"  center_x = {center_x:.4f}")
        debug_print(f"  center_y = {center_y:.4f}")

        try:
            # 参数验证
            if x_length <= 0 or y_length <= 0:
                debug_print("✗ 参数错误: 长度必须大于0")
                raise ValueError("长度必须大于0")
            if x_pitch <= 0 or y_pitch <= 0:
                debug_print("✗ 参数错误: 间距必须大于0")
                raise ValueError("间距必须大于0")

            # 保存参数
            self.x_pitch = x_pitch
            self.y_pitch = y_pitch
            self.center_x = center_x
            self.center_y = center_y

            # 计算边界
            self.x_min = center_x - x_length / 2.0
            self.x_max = center_x + x_length / 2.0
            self.y_min = center_y - y_length / 2.0
            self.y_max = center_y + y_length / 2.0

            debug_print(f"计算边界:")
            debug_print(f"  x_min = {self.x_min:.4f}")
            debug_print(f"  x_max = {self.x_max:.4f}")
            debug_print(f"  y_min = {self.y_min:.4f}")
            debug_print(f"  y_max = {self.y_max:.4f}")

            # 生成网格点
            self.points = []

            # 计算点的数量
            num_x = int(round(x_length / x_pitch)) + 1
            num_y = int(round(y_length / y_pitch)) + 1

            debug_print(f"网格规模:")
            debug_print(f"  num_x = {num_x}")
            debug_print(f"  num_y = {num_y}")
            debug_print(f"  预计总点数 = {num_x * num_y}")

            # 生成所有点(从左下角开始)
            point_count = 0
            for i in range(num_y):
                y = self.y_min + i * y_pitch
                for j in range(num_x):
                    x = self.x_min + j * x_pitch
                    self.points.append((x, y))
                    point_count += 1

                    if DEBUG_MODE and point_count <= 3:  # 只打印前3个点
                        debug_print(f"  生成点 {point_count-1}: ({x:.4f}, {y:.4f})")

            debug_print(f"✓ generate_rectangular_map() 成功完成")
            debug_print(f"  实际生成点数: {len(self.points)}")
            return True
        except Exception as e:
            debug_print(f"✗ generate_rectangular_map() 执行失败: {e}")
            return False

    def _calculate_boundaries(self):
        """计算点集的边界和中心"""
        debug_print(f"_calculate_boundaries() 开始执行")
        if not self.points:
            debug_print("  警告: 点列表为空")
            return

        x_values = [p[0] for p in self.points]
        y_values = [p[1] for p in self.points]

        self.x_min = min(x_values)
        self.x_max = max(x_values)
        self.y_min = min(y_values)
        self.y_max = max(y_values)

        # 估算中心点
        self.center_x = (self.x_min + self.x_max) / 2.0
        self.center_y = (self.y_min + self.y_max) / 2.0

        # 估算pitch
        unique_x = sorted(set([round(x, 6) for x in x_values]))
        unique_y = sorted(set([round(y, 6) for y in y_values]))

        if len(unique_x) > 1:
            self.x_pitch = unique_x[1] - unique_x[0]
        if len(unique_y) > 1:
            self.y_pitch = unique_y[1] - unique_y[0]

        debug_print(f"  边界计算完成:")
        debug_print(f"    X范围: [{self.x_min:.4f}, {self.x_max:.4f}]")
        debug_print(f"    Y范围: [{self.y_min:.4f}, {self.y_max:.4f}]")
        debug_print(f"    中心点: ({self.center_x:.4f}, {self.center_y:.4f})")
        debug_print(f"    Pitch: x={self.x_pitch:.4f}, y={self.y_pitch:.4f}")

    def get_points(self) -> List[Tuple[float, float]]:
        """获取所有点"""
        debug_print(f"get_points() 返回 {len(self.points)} 个点")
        return self.points

    def get_boundaries(self) -> Dict[str, float]:
        """获取边界信息"""
        return {
            'x_min': self.x_min,
            'x_max': self.x_max,
            'y_min': self.y_min,
            'y_max': self.y_max,
            'center_x': self.center_x,
            'center_y': self.center_y
        }

    def get_pitch(self) -> Tuple[float, float]:
        """获取间距"""
        return (self.x_pitch, self.y_pitch)

    def add_point(self, x: float, y: float):
        """添加一个点"""
        debug_print(f"\nadd_point() 执行")
        debug_print(f"  添加点: ({x:.4f}, {y:.4f})")
        self.points.append((x, y))
        self._calculate_boundaries()
        debug_print(f"✓ 添加完成,当前总点数: {len(self.points)}")

    def delete_point(self, index: int) -> bool:
        """
        删除指定索引的点

        Args:
            index: 点的索引

        Returns:
            bool: 成功返回True
        """
        debug_print(f"\ndelete_point() 执行")
        debug_print(f"  删除索引: {index}")

        try:
            if 0 <= index < len(self.points):
                old_point = self.points[index]
                self.points.pop(index)
                self._calculate_boundaries()
                debug_print(f"✓ 删除成功: 删除了点 ({old_point[0]:.4f}, {old_point[1]:.4f})")
                debug_print(f"  剩余点数: {len(self.points)}")
                return True
            debug_print(f"✗ 删除失败: 索引 {index} 超出范围 [0, {len(self.points)-1}]")
            return False
        except Exception as e:
            debug_print(f"✗ delete_point() 执行失败: {e}")
            return False

    def update_point(self, index: int, new_x: float, new_y: float) -> bool:
        """
        更新指定索引的点

        Args:
            index: 点的索引
            new_x: 新的X坐标
            new_y: 新的Y坐标

        Returns:
            bool: 成功返回True
        """
        debug_print(f"\nupdate_point() 执行")
        debug_print(f"  索引: {index}")
        debug_print(f"  新坐标: ({new_x:.4f}, {new_y:.4f})")

        try:
            if 0 <= index < len(self.points):
                old_point = self.points[index]
                self.points[index] = (new_x, new_y)
                self._calculate_boundaries()
                debug_print(f"✓ 更新成功:")
                debug_print(f"    旧坐标: ({old_point[0]:.4f}, {old_point[1]:.4f})")
                debug_print(f"    新坐标: ({new_x:.4f}, {new_y:.4f})")
                return True
            debug_print(f"✗ 更新失败: 索引 {index} 超出范围 [0, {len(self.points)-1}]")
            return False
        except Exception as e:
            debug_print(f"✗ update_point() 执行失败: {e}")
            return False

    def find_nearest_point(self, x: float, y: float, threshold: float = 5.0) -> Optional[int]:
        """
        查找最近的点(在阈值范围内)

        Args:
            x: 查询点X坐标
            y: 查询点Y坐标
            threshold: 距离阈值

        Returns:
            Optional[int]: 找到返回索引,否则返回None
        """
        if not self.points:
            return None

        min_dist = float('inf')
        nearest_index = None

        for i, (px, py) in enumerate(self.points):
            dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest_index = i

        if min_dist <= threshold:
            return nearest_index
        return None

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.points:
            return {
                'total_points': 0,
                'x_range': (0, 0),
                'y_range': (0, 0),
                'center': (0, 0)
            }

        return {
            'total_points': len(self.points),
            'x_range': (self.x_min, self.x_max),
            'y_range': (self.y_min, self.y_max),
            'center': (self.center_x, self.center_y),
            'x_pitch': self.x_pitch,
            'y_pitch': self.y_pitch
        }

    def save_to_csv(self, file_path: str, decimal_places: int = 6) -> bool:
        """
        保存到CSV文件

        Args:
            file_path: 保存路径
            decimal_places: 小数位数

        Returns:
            bool: 成功返回True
        """
        debug_print(f"\nsave_to_csv() 开始执行")
        debug_print(f"  保存路径: '{file_path}'")
        debug_print(f"  小数位数: {decimal_places}")
        debug_print(f"  点数: {len(self.points)}")

        try:
            data = []
            for idx, (x, y) in enumerate(self.points):
                x_str = f"{x:.{decimal_places}f}".rstrip('0').rstrip('.')
                y_str = f"{y:.{decimal_places}f}".rstrip('0').rstrip('.')
                data.append({'X': x_str, 'Y': y_str})

                if DEBUG_MODE and idx < 3:  # 只打印前3个点
                    debug_print(f"  保存点 {idx}: X={x_str}, Y={y_str}")

            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            debug_print(f"✓ save_to_csv() 成功完成")
            debug_print(f"  已保存 {len(data)} 行数据到 '{file_path}'")
            return True
        except Exception as e:
            debug_print(f"✗ save_to_csv() 执行失败: {e}")
            return False

    def clear(self):
        """清空数据"""
        debug_print(f"\nclear() 执行 - 清空所有数据")
        self.points = []
        self.center_x = 0.0
        self.center_y = 0.0
        self.x_min = 0.0
        self.x_max = 0.0
        self.y_min = 0.0
        self.y_max = 0.0
        self.x_pitch = 1.0
        self.y_pitch = 1.0
        debug_print(f"✓ 数据已清空")
