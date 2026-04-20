"""
Map建立核心功能模块
负责生成晶圆Map坐标点数据
"""

import pandas as pd
from typing import List, Tuple, Dict
import math

# 调试标志
DEBUG_MODE = True

def debug_print(msg: str):
    """调试输出函数"""
    if DEBUG_MODE:
        print(f"[CORE] {msg}")


class MapEstablishProcessor:
    """Map建立处理器"""

    def __init__(self):
        self.wafer_sizes = {
            "4 inch": 100.0,  # 直径100mm，半径50mm
            "6 inch": 150.0,  # 直径150mm，半径75mm
            "8 inch": 200.0   # 直径200mm，半径100mm
        }

    def get_radius(self, wafer_size: str) -> float:
        """
        获取晶圆半径

        Args:
            wafer_size: 晶圆尺寸字符串（"4 inch", "6 inch", "8 inch"）

        Returns:
            float: 半径（mm）
        """
        diameter = self.wafer_sizes.get(wafer_size, 200.0)
        return diameter / 2.0

    def generate_grid_points(self, ref_x: float, ref_y: float,
                            x_pitch: float, y_pitch: float,
                            radius: float) -> List[Tuple[float, float, float, float]]:
        """
        生成圆形区域内的网格点

        Args:
            ref_x: 参考点X坐标
            ref_y: 参考点Y坐标
            x_pitch: X方向间距
            y_pitch: Y方向间距
            radius: 晶圆半径

        Returns:
            List[Tuple]: 网格点列表，每个点为 (x, y, grid_x, grid_y)
                        grid_x, grid_y 是网格索引（整数）
        """
        debug_print("="*50)
        debug_print("generate_grid_points() 开始执行")
        debug_print(f"输入参数 - ref_x: {ref_x}, ref_y: {ref_y}")
        debug_print(f"输入参数 - x_pitch: {x_pitch}, y_pitch: {y_pitch}")
        debug_print(f"输入参数 - radius: {radius}")

        # 参数验证
        if x_pitch <= 0 or y_pitch <= 0:
            debug_print(f"错误：间距必须大于0 (x_pitch={x_pitch}, y_pitch={y_pitch})")
            raise ValueError(f"间距必须大于0 (x_pitch={x_pitch}, y_pitch={y_pitch})")

        if radius <= 0:
            debug_print(f"错误：半径必须大于0 (radius={radius})")
            raise ValueError(f"半径必须大于0 (radius={radius})")

        points = []

        # 计算网格范围（确保覆盖整个圆）
        x_range = int(math.ceil(radius / x_pitch)) + 1
        y_range = int(math.ceil(radius / y_pitch)) + 1
        debug_print(f"计算网格范围 - x_range: {x_range}, y_range: {y_range}")

        # 生成所有可能的网格点
        total_checked = 0
        for m in range(-x_range, x_range + 1):
            for n in range(-y_range, y_range + 1):
                total_checked += 1
                x = ref_x + m * x_pitch
                y = ref_y + n * y_pitch

                # 检查点是否在圆内
                if x * x + y * y < radius * radius:
                    points.append((x, y, m, n))

        debug_print(f"检查了 {total_checked} 个点，保留 {len(points)} 个在圆内的点")
        debug_print("generate_grid_points() 执行完成")
        debug_print("="*50)
        return points

    def get_boundaries(self, points: List[Tuple[float, float, float, float]]) -> Dict[str, float]:
        """
        获取网格点的边界值

        Args:
            points: 网格点列表

        Returns:
            Dict: 包含 x_min, x_max, y_min, y_max 的字典
        """
        if not points:
            return {"x_min": 0.0, "x_max": 0.0, "y_min": 0.0, "y_max": 0.0}

        x_values = [p[0] for p in points]
        y_values = [p[1] for p in points]

        return {
            "x_min": min(x_values),
            "x_max": max(x_values),
            "y_min": min(y_values),
            "y_max": max(y_values)
        }

    def generate_scan_path(self, points: List[Tuple[float, float, float, float]],
                          start_position: str, scan_direction: str,
                          boundaries: Dict[str, float]) -> List[Tuple[float, float]]:
        """
        生成蛇形扫描路径

        新逻辑：扫描整个正方形区域，然后过滤掉圆外的点

        Args:
            points: 网格点列表（未使用）
            start_position: 起点位置（"左上", "右上", "左下", "右下"）
            scan_direction: 扫描方向（"X方向", "Y方向"）
            boundaries: 边界值字典

        Returns:
            List[Tuple]: 按扫描顺序排列的点列表 (x, y)
        """
        # 从边界获取半径
        radius = max(abs(boundaries['x_min']), abs(boundaries['x_max']),
                    abs(boundaries['y_min']), abs(boundaries['y_max']))

        # 获取起点（固定的4个角点）
        start_point = self._get_start_point(start_position, radius)

        # 获取pitch（从边界计算）
        if points:
            x_values = sorted(set(p[0] for p in points))
            y_values = sorted(set(p[1] for p in points))
            if len(x_values) > 1:
                x_pitch = x_values[1] - x_values[0]
            else:
                x_pitch = 2.0
            if len(y_values) > 1:
                y_pitch = y_values[1] - y_values[0]
            else:
                y_pitch = 2.0
        else:
            x_pitch = 2.0
            y_pitch = 2.0

        # 按方向生成路径
        if scan_direction == "X方向":
            scan_path = self._generate_x_scan_path_simple(start_point, radius, x_pitch, y_pitch)
        else:
            scan_path = self._generate_y_scan_path_simple(start_point, radius, x_pitch, y_pitch)

        # 过滤掉圆外的点
        filtered_path = [(x, y) for x, y in scan_path if x*x + y*y < radius*radius]

        debug_print(f"[扫描路径] 总扫描点数: {len(scan_path)}, 圆内点数: {len(filtered_path)}")

        # 如果过滤后有数据，返回圆内的点（CSV只包含圆内的点）
        return filtered_path

    def _get_start_point(self, start_position: str, radius: float) -> Tuple[float, float]:
        """
        获取起点坐标（固定的4个角点）

        新逻辑：直接使用晶圆的4个角作为起点，不管该点是否在圆内

        Args:
            start_position: 起点位置（"左上", "右上", "左下", "右下"）
            radius: 晶圆半径

        Returns:
            Tuple: (x, y) 起点坐标
        """
        if start_position == "左上":
            result = (-radius, radius)
        elif start_position == "右上":
            result = (radius, radius)
        elif start_position == "左下":
            result = (-radius, -radius)
        elif start_position == "右下":
            result = (radius, -radius)
        else:
            result = (-radius, radius)  # 默认左上

        debug_print(f"[起点] 位置:{start_position}, 起点:{result}")
        return result

    def _generate_x_scan_path_simple(self, start_point: Tuple[float, float],
                                     radius: float, x_pitch: float, y_pitch: float) -> List[Tuple[float, float]]:
        """
        生成X方向蛇形扫描路径（简化版）

        新逻辑：
        1. 从起点开始
        2. 沿X方向蛇形扫描整个正方形区域(-r到+r)
        3. 返回所有扫描点（包括圆外的点，由调用者过滤）

        Args:
            start_point: 起点坐标
            radius: 半径
            x_pitch: X方向间距
            y_pitch: Y方向间距

        Returns:
            List[Tuple]: 扫描路径点列表
        """
        path = []

        # 生成所有Y值（从-r到+r）
        y_values = []
        y = -radius
        while y <= radius + 0.001:  # 考虑浮点误差
            y_values.append(y)
            y += y_pitch

        # 生成所有X值（从-r到+r）
        x_values = []
        x = -radius
        while x <= radius + 0.001:
            x_values.append(x)
            x += x_pitch

        debug_print(f"[X扫描] 正方形区域: X({x_values[0]:.2f}~{x_values[-1]:.2f}), Y({y_values[0]:.2f}~{y_values[-1]:.2f})")
        debug_print(f"[X扫描] 起点: {start_point}")

        # 确定第一行的扫描方向
        start_x = start_point[0]
        x_mid = 0  # 正方形区域的中点X
        forward = start_x <= x_mid  # 起点在左侧或中间，从左到右

        debug_print(f"[X扫描] 第一行方向: {'左→右' if forward else '右→左'}")

        # 从靠近起点的Y值开始遍历
        start_y = start_point[1]
        y_indices = list(range(len(y_values)))
        if start_y > 0:
            # 从上往下，Y从大到小
            y_indices.reverse()

        # 蛇形扫描每一行
        for i, y_index in enumerate(y_indices):
            y = y_values[y_index]

            # 获取当前行的所有X点
            row_x = x_values[:]  # 复制一份

            # 根据方向排序
            if not forward:
                row_x.reverse()  # 从右到左

            # 添加到路径
            for x in row_x:
                path.append((x, y))

            # 下一行反向
            forward = not forward

        return path

    def _generate_y_scan_path_simple(self, start_point: Tuple[float, float],
                                     radius: float, x_pitch: float, y_pitch: float) -> List[Tuple[float, float]]:
        """
        生成Y方向蛇形扫描路径（简化版）

        新逻辑：
        1. 从起点开始
        2. 沿Y方向蛇形扫描整个正方形区域(-r到+r)
        3. 返回所有扫描点（包括圆外的点，由调用者过滤）

        Args:
            start_point: 起点坐标
            radius: 半径
            x_pitch: X方向间距
            y_pitch: Y方向间距

        Returns:
            List[Tuple]: 扫描路径点列表
        """
        path = []

        # 生成所有Y值（从-r到+r）
        y_values = []
        y = -radius
        while y <= radius + 0.001:
            y_values.append(y)
            y += y_pitch

        # 生成所有X值（从-r到+r）
        x_values = []
        x = -radius
        while x <= radius + 0.001:
            x_values.append(x)
            x += x_pitch

        debug_print(f"[Y扫描] 正方形区域: X({x_values[0]:.2f}~{x_values[-1]:.2f}), Y({y_values[0]:.2f}~{y_values[-1]:.2f})")
        debug_print(f"[Y扫描] 起点: {start_point}")

        # 确定第一列的扫描方向
        start_y = start_point[1]
        y_mid = 0  # 正方形区域的中点Y
        forward = start_y > y_mid  # 起点在上侧或中间，从上到下

        debug_print(f"[Y扫描] 第一列方向: {'上→下' if forward else '下→上'}")

        # 从靠近起点的X值开始遍历
        start_x = start_point[0]
        x_indices = list(range(len(x_values)))
        if start_x > 0:
            # 从右往左，X从大到小
            x_indices.reverse()

        # 蛇形扫描每一列
        for i, x_index in enumerate(x_indices):
            x = x_values[x_index]

            # 获取当前列的所有Y点
            col_y = y_values[:]  # 复制一份

            # 根据方向排序
            if forward:
                col_y.reverse()  # 从上到下：Y从大到小
            # else: 从小到大，不需要reverse

            # 添加到路径
            for y in col_y:
                path.append((x, y))

            # 下一列反向
            forward = not forward

        return path

    def _generate_x_scan_path(self, point_dict: Dict[Tuple[float, float], Tuple[float, float]],
                              start_point: Tuple[float, float],
                              boundaries: Dict[str, float]) -> List[Tuple[float, float]]:
        """
        生成X方向蛇形扫描路径

        Args:
            point_dict: 点字典
            start_point: 起点
            boundaries: 边界值

        Returns:
            List[Tuple]: 扫描路径
        """
        path = []

        # 获取所有唯一的Y值并排序
        y_values = sorted(set(p[1] for p in point_dict.values()))
        x_values = sorted(set(p[0] for p in point_dict.values()))

        debug_print(f"[X扫描] 唯一Y值数量: {len(y_values)}, 范围: {y_values[0]:.2f} ~ {y_values[-1]:.2f}")
        debug_print(f"[X扫描] 唯一X值数量: {len(x_values)}, 范围: {x_values[0]:.2f} ~ {x_values[-1]:.2f}")

        # 确定扫描方向
        start_y = start_point[1]
        start_x = start_point[0]

        # 根据起点的X位置确定第一行的扫描方向
        # 如果起点在左侧，第一行从左到右；如果在右侧，第一行从右到左
        x_values_sorted = sorted(set(p[0] for p in point_dict.values()))
        x_mid = (x_values_sorted[0] + x_values_sorted[-1]) / 2
        forward = start_x < x_mid  # True表示从左到右

        debug_print(f"[X扫描] 起点=({start_x:.2f}, {start_y:.2f}), X中点={x_mid:.2f}, 第一行方向={'左→右' if forward else '右→左'}")

        # 从靠近起点的Y值开始
        if start_y in y_values:
            start_index = y_values.index(start_y)
        else:
            # 找到最接近的Y值
            start_index = min(range(len(y_values)),
                            key=lambda i: abs(y_values[i] - start_y))

        debug_print(f"[X扫描] 起点Y={start_y:.2f}, 在y_values中的索引: {start_index}")

        # 根据起点位置确定Y的遍历顺序
        if start_y <= boundaries['y_min']:
            # 从底部开始，向上扫描
            y_indices_to_visit = list(range(len(y_values)))
        elif start_y >= boundaries['y_max']:
            # 从顶部开始，向下扫描
            y_indices_to_visit = list(range(len(y_values)-1, -1, -1))
        else:
            # 从中间开始，蛇形遍历所有Y值
            y_indices_to_visit = []
            up = True
            current = start_index
            visited = set()

            while len(visited) < len(y_values):
                if 0 <= current < len(y_values) and current not in visited:
                    y_indices_to_visit.append(current)
                    visited.add(current)

                if up:
                    current += 1
                    if current >= len(y_values):
                        current = start_index - 1
                        up = False
                else:
                    current -= 1
                    if current < 0:
                        break

        debug_print(f"[X扫描] 将访问 {len(y_indices_to_visit)} 个Y值")

        # 遍历每一行
        for idx, y_index in enumerate(y_indices_to_visit):
            if not (0 <= y_index < len(y_values)):
                continue

            y = y_values[y_index]

            # 获取当前行的所有X点
            row_points = []
            for x in x_values:
                if (round(x, 6), round(y, 6)) in point_dict:
                    row_points.append(x)

            # 根据方向排序
            if forward:
                row_points.sort()
            else:
                row_points.sort(reverse=True)

            # 添加到路径
            for x in row_points:
                path.append((x, y))

            # 下一行反向
            forward = not forward

        debug_print(f"[X扫描] 生成的路径点数: {len(path)}")
        return path

    def _generate_y_scan_path(self, point_dict: Dict[Tuple[float, float], Tuple[float, float]],
                              start_point: Tuple[float, float],
                              boundaries: Dict[str, float]) -> List[Tuple[float, float]]:
        """
        生成Y方向蛇形扫描路径

        Args:
            point_dict: 点字典
            start_point: 起点
            boundaries: 边界值

        Returns:
            List[Tuple]: 扫描路径
        """
        path = []

        # 获取所有唯一的X值并排序
        x_values = sorted(set(p[0] for p in point_dict.values()))
        y_values = sorted(set(p[1] for p in point_dict.values()))

        debug_print(f"[Y扫描] 唯一X值数量: {len(x_values)}, 范围: {x_values[0]:.2f} ~ {x_values[-1]:.2f}")
        debug_print(f"[Y扫描] 唯一Y值数量: {len(y_values)}, 范围: {y_values[0]:.2f} ~ {y_values[-1]:.2f}")

        # 确定扫描方向
        start_x = start_point[0]
        start_y = start_point[1]

        # 根据起点的Y位置确定第一列的扫描方向
        # 如果起点在上侧，第一列从上到下；如果在下侧，第一列从下到上
        y_values_sorted = sorted(set(p[1] for p in point_dict.values()))
        y_mid = (y_values_sorted[0] + y_values_sorted[-1]) / 2
        forward = start_y > y_mid  # True表示从上到下

        debug_print(f"[Y扫描] 起点=({start_x:.2f}, {start_y:.2f}), Y中点={y_mid:.2f}, 第一列方向={'上→下' if forward else '下→上'}")

        # 从靠近起点的X值开始
        if start_x in x_values:
            start_index = x_values.index(start_x)
        else:
            # 找到最接近的X值
            start_index = min(range(len(x_values)),
                            key=lambda i: abs(x_values[i] - start_x))

        debug_print(f"[Y扫描] 起点X={start_x:.2f}, 在x_values中的索引: {start_index}")

        # 根据起点位置确定X的遍历顺序
        if start_x <= boundaries['x_min']:
            # 从左侧开始，向右扫描
            x_indices_to_visit = list(range(len(x_values)))
        elif start_x >= boundaries['x_max']:
            # 从右侧开始，向左扫描
            x_indices_to_visit = list(range(len(x_values)-1, -1, -1))
        else:
            # 从中间开始，蛇形遍历所有X值
            x_indices_to_visit = []
            right = True
            current = start_index
            visited = set()

            while len(visited) < len(x_values):
                if 0 <= current < len(x_values) and current not in visited:
                    x_indices_to_visit.append(current)
                    visited.add(current)

                if right:
                    current += 1
                    if current >= len(x_values):
                        current = start_index - 1
                        right = False
                else:
                    current -= 1
                    if current < 0:
                        break

        debug_print(f"[Y扫描] 将访问 {len(x_indices_to_visit)} 个X值")

        # 遍历每一列
        for idx, x_index in enumerate(x_indices_to_visit):
            if not (0 <= x_index < len(x_values)):
                continue

            x = x_values[x_index]

            # 获取当前列的所有Y点
            col_points = []
            for y in y_values:
                if (round(x, 6), round(y, 6)) in point_dict:
                    col_points.append(y)

            # 根据方向排序
            # forward=True表示从上到下（Y从大到小），forward=False表示从下到上（Y从小到大）
            if forward:
                col_points.sort(reverse=True)  # 从上到下：Y从大到小
            else:
                col_points.sort()  # 从下到上：Y从小到大

            # 添加到路径
            for y in col_points:
                path.append((x, y))

            # 下一列反向
            forward = not forward

        debug_print(f"[Y扫描] 生成的路径点数: {len(path)}")
        return path

    def determine_decimal_places(self, value: float) -> int:
        """
        确定数值的小数位数
        注意：这个方法用于从用户输入的字符串格式推断精度

        Args:
            value: 输入值

        Returns:
            int: 小数位数
        """
        # 转换为字符串并检查小数位
        # Python的str()可能会截断末尾的0，所以我们需要特殊处理
        value_str = f"{value:f}"  # 使用%f格式化保留完整小数位
        if '.' in value_str:
            decimal_part = value_str.split('.')[1].rstrip('0')
            return len(decimal_part) if decimal_part else 0
        return 0

    def format_coordinate(self, value: float, decimal_places: int) -> str:
        """
        格式化坐标值

        Args:
            value: 坐标值
            decimal_places: 小数位数

        Returns:
            str: 格式化后的字符串
        """
        return f"{value:.{decimal_places}f}"

    def generate_map_data(self, wafer_size: str, ref_x: float, ref_y: float,
                         x_pitch: float, y_pitch: float, start_position: str,
                         scan_direction: str) -> Tuple[List[Tuple[float, float]], Dict]:
        """
        生成完整的Map数据（简化版本）

        策略：
        1. 从4个角点开始扫描整个正方形区域[-r, r] × [-r, r]
        2. 蛇形遍历所有点
        3. 过滤掉圆外的点（x² + y² < r²）
        4. 只返回圆内的点用于CSV输出

        Args:
            wafer_size: 晶圆尺寸
            ref_x: 参考点X坐标（暂未使用，保留以备将来功能扩展）
            ref_y: 参考点Y坐标（暂未使用，保留以备将来功能扩展）
            x_pitch: X方向间距
            y_pitch: Y方向间距
            start_position: 起点位置（左上/右上/左下/右下）
            scan_direction: 扫描方向（X方向/Y方向）

        Returns:
            Tuple: (扫描路径点列表（仅圆内点）, 统计信息字典)
        """
        debug_print("\n" + "="*60)
        debug_print("generate_map_data() 开始执行（简化版本）")
        debug_print(f"完整参数列表（按函数定义顺序）:")
        debug_print(f"  wafer_size: {wafer_size} (type: {type(wafer_size).__name__})")
        debug_print(f"  ref_x: {ref_x} (type: {type(ref_x).__name__})")
        debug_print(f"  ref_y: {ref_y} (type: {type(ref_y).__name__})")
        debug_print(f"  x_pitch: {x_pitch} (type: {type(x_pitch).__name__})")
        debug_print(f"  y_pitch: {y_pitch} (type: {type(y_pitch).__name__})")
        debug_print(f"  start_position: {start_position} (type: {type(start_position).__name__})")
        debug_print(f"  scan_direction: {scan_direction} (type: {type(scan_direction).__name__})")

        try:
            # 获取半径
            radius = self.get_radius(wafer_size)
            debug_print(f"获取晶圆半径: {radius}mm")

            # 获取起点（固定的4个角点）
            start_point = self._get_start_point(start_position, radius)
            debug_print(f"起点: {start_point}")

            # 生成扫描路径（扫描整个正方形区域）
            debug_print(f"生成{scan_direction}扫描路径（扫描整个正方形区域）...")
            if scan_direction == "X方向":
                scan_path = self._generate_x_scan_path_simple(start_point, radius, x_pitch, y_pitch)
            else:  # Y方向
                scan_path = self._generate_y_scan_path_simple(start_point, radius, x_pitch, y_pitch)

            debug_print(f"扫描路径生成完成，正方形区域共 {len(scan_path)} 个点")

            # 过滤掉圆外的点
            debug_print("过滤圆外的点...")
            filtered_path = [(x, y) for x, y in scan_path if x*x + y*y < radius*radius]
            debug_print(f"过滤后，圆内剩余 {len(filtered_path)} 个点")

            if not filtered_path:
                debug_print("警告：过滤后没有剩余点！")
                raise ValueError("过滤后没有剩余点，请检查参数设置")

            # 计算统计信息（基于过滤后的点）
            x_values = [p[0] for p in filtered_path]
            y_values = [p[1] for p in filtered_path]
            boundaries = {
                "x_min": min(x_values),
                "x_max": max(x_values),
                "y_min": min(y_values),
                "y_max": max(y_values)
            }

            stats = {
                "total_points": len(filtered_path),
                "radius": radius,
                "boundaries": boundaries,
                "wafer_size": wafer_size,
                "x_pitch": x_pitch,
                "y_pitch": y_pitch,
                "start_position": start_position,
                "scan_direction": scan_direction
            }

            debug_print(f"统计信息 - 总点数: {stats['total_points']}")
            debug_print(f"统计信息 - 边界: X({boundaries['x_min']:.2f}~{boundaries['x_max']:.2f}), "
                       f"Y({boundaries['y_min']:.2f}~{boundaries['y_max']:.2f})")
            debug_print(f"统计信息 - 起点: {filtered_path[0] if filtered_path else 'N/A'}")
            debug_print(f"统计信息 - 终点: {filtered_path[-1] if filtered_path else 'N/A'}")

            debug_print("generate_map_data() 执行成功")
            debug_print("="*60 + "\n")
            return filtered_path, stats

        except Exception as e:
            debug_print(f"错误：generate_map_data() 执行失败")
            debug_print(f"异常信息: {e}")
            debug_print(f"异常类型: {type(e).__name__}")
            import traceback
            debug_print(f"完整堆栈:\n{traceback.format_exc()}")
            debug_print("="*60 + "\n")
            raise

    def save_to_csv(self, scan_path: List[Tuple[float, float]],
                   file_path: str, decimal_places: int) -> bool:
        """
        保存扫描路径到CSV文件

        Args:
            scan_path: 扫描路径点列表
            file_path: 保存文件路径
            decimal_places: 小数位数

        Returns:
            bool: 成功返回True
        """
        try:
            # 准备数据
            data = []
            for x, y in scan_path:
                x_str = self.format_coordinate(x, decimal_places)
                y_str = self.format_coordinate(y, decimal_places)
                data.append((x_str, y_str))

            # 创建DataFrame并保存
            df = pd.DataFrame(data, columns=["X", "Y"])
            df.to_csv(file_path, index=False)

            return True
        except Exception as e:
            print(f"保存CSV文件失败：{str(e)}")
            return False
