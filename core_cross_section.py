"""
核心功能模块
负责处理CSV数据读取和坐标查询逻辑
"""

import pandas as pd
from typing import Union, List, Tuple


class MapDataProcessor:
    """地图数据处理器"""

    def __init__(self):
        self.data = None
        self.file_path = None
        self.x_col = None
        self.y_col = None
        self.thickness_col = None

    def load_csv(self, file_path: str) -> bool:
        """
        加载CSV文件

        Args:
            file_path: CSV文件路径

        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            self.file_path = file_path
            self.data = pd.read_csv(file_path)

            # 获取列名（假设前两列是X和Y坐标，第三列是膜厚）
            columns = self.data.columns.tolist()
            if len(columns) >= 3:
                self.x_col = columns[0]
                self.y_col = columns[1]
                self.thickness_col = columns[2]
                return True
            else:
                print(f"错误：CSV文件至少需要3列，当前只有{len(columns)}列")
                return False
        except Exception as e:
            print(f"加载CSV文件失败：{str(e)}")
            return False

    def get_data_info(self) -> Tuple[str, str, str]:
        """
        获取数据列信息

        Returns:
            Tuple: (x列名, y列名, 膜厚列名)
        """
        return self.x_col, self.y_col, self.thickness_col

    def search_by_x(self, x_value: float, tolerance: float = 1e-6) -> List[Tuple[float, float, float]]:
        """
        根据X坐标搜索所有匹配的点

        Args:
            x_value: 要搜索的X坐标值
            tolerance: 浮点数比较容差

        Returns:
            List[Tuple]: 包含(x, y, thickness)的列表
        """
        if self.data is None:
            print("错误：未加载数据，请先加载CSV文件")
            return []

        # 查找匹配的点（考虑浮点数精度）
        mask = abs(self.data[self.x_col] - x_value) < tolerance
        result_df = self.data[mask]

        if len(result_df) == 0:
            print(f"警告：未找到X坐标为 {x_value} 的点")
            return []

        # 转换为列表返回
        results = []
        for _, row in result_df.iterrows():
            results.append((
                float(row[self.x_col]),
                float(row[self.y_col]),
                float(row[self.thickness_col])
            ))

        return results

    def search_by_y(self, y_value: float, tolerance: float = 1e-6) -> List[Tuple[float, float, float]]:
        """
        根据Y坐标搜索所有匹配的点

        Args:
            y_value: 要搜索的Y坐标值
            tolerance: 浮点数比较容差

        Returns:
            List[Tuple]: 包含(x, y, thickness)的列表
        """
        if self.data is None:
            print("错误：未加载数据，请先加载CSV文件")
            return []

        # 查找匹配的点（考虑浮点数精度）
        mask = abs(self.data[self.y_col] - y_value) < tolerance
        result_df = self.data[mask]

        if len(result_df) == 0:
            print(f"警告：未找到Y坐标为 {y_value} 的点")
            return []

        # 转换为列表返回
        results = []
        for _, row in result_df.iterrows():
            results.append((
                float(row[self.x_col]),
                float(row[self.y_col]),
                float(row[self.thickness_col])
            ))

        return results

    def get_x_values(self) -> List[float]:
        """
        获取所有唯一的X坐标值

        Returns:
            List[float]: 排序后的唯一X坐标列表
        """
        if self.data is None:
            return []
        return sorted(self.data[self.x_col].unique().tolist())

    def get_y_values(self) -> List[float]:
        """
        获取所有唯一的Y坐标值

        Returns:
            List[float]: 排序后的唯一Y坐标列表
        """
        if self.data is None:
            return []
        return sorted(self.data[self.y_col].unique().tolist())

    def get_data_summary(self) -> str:
        """
        获取数据摘要信息

        Returns:
            str: 数据摘要字符串
        """
        if self.data is None:
            return "未加载数据"

        x_col, y_col, thickness_col = self.get_data_info()
        summary = f"""
文件路径: {self.file_path}
数据点总数: {len(self.data)}
X列名: {x_col}
Y列名: {y_col}
膜厚列名: {thickness_col}
X坐标范围: {self.data[x_col].min():.2f} ~ {self.data[x_col].max():.2f}
Y坐标范围: {self.data[y_col].min():.2f} ~ {self.data[y_col].max():.2f}
膜厚范围: {self.data[thickness_col].min():.2f} ~ {self.data[thickness_col].max():.2f}
"""
        return summary.strip()
