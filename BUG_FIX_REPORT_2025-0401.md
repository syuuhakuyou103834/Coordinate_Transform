# Bug修复报告 - 2025-04-01

## Bug描述

### 错误信息
```
Traceback (most recent call last):
  File "D:\VScode_Project\Coordinate_Transform\ui_fine_map_revision.py", line 117, in paintEvent
    self._draw_axes(painter)
    ~~~~~~~~~~~~~~~^^^^^^^^^
  File "D:\VScode_Project\Coordinate_Transform\ui_fine_map_revision.py", line 193, in _draw_axes
    painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5, int(p.y())))
                                                         ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: int() base must be >= 2 and <= 36, or 0
```

### 错误原因
在`ui_fine_map_revision.py`的第193行,`drawLine`方法的调用中,括号位置错误:

```python
# 错误的代码
painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5, int(p.y())))
```

问题在于 `int(origin_screen.x() - 5, int(p.y()))` 这个表达式被错误地解析为 `int()` 函数的两个参数,而不是两个独立的参数传递给 `drawLine`。

### 触发条件
当用户创建新的Map并触发可视化图绘制时,程序尝试绘制Y轴刻度线,此时发生参数解析错误导致程序崩溃。

## 修复方案

### 修改文件
`D:\VScode_Project\Coordinate_Transform\ui_fine_map_revision.py`

### 修改位置
第193行,`_draw_axes`方法中的Y轴刻度绘制部分

### 修改前
```python
painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5, int(p.y())))
```

### 修改后
```python
painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5), int(p.y()))
```

### 修复说明
将 `int(origin_screen.x() - 5, int(p.y()))` 修改为两个独立的参数:
- `int(origin_screen.x() - 5)`
- `int(p.y())`

## 测试验证

### 测试步骤
1. 启动程序 `python main.py`
2. 在精细Map修订工具窗口中
3. 点击菜单: 数据 → 新建Map
4. 输入参数(例如: 14x12mm, 间距2mm, 中心(0,0))
5. 点击确定

### 预期结果
✅ Map成功创建
✅ 可视化图正常显示
✅ 坐标轴和刻度正确绘制
✅ 点位正确显示
✅ 表格数据正确显示
✅ 程序不崩溃

### 实际结果
✅ 程序成功启动
✅ 创建Map功能正常
✅ 可视化图绘制成功
✅ 无错误或异常

## 影响范围

### 影响的代码
- 文件: `ui_fine_map_revision.py`
- 方法: `MapViewWidget._draw_axes()`
- 行号: 193

### 影响的功能
- Map可视化图的Y轴刻度绘制
- 所有需要绘制Y轴刻度的场景:
  - 新建Map
  - 导入CSV
  - 重绘视图

### 严重程度
**中等** - 会导致程序崩溃,但只影响可视化功能,不影响数据处理

## 根本原因分析

### 为什么会出现这个错误?
在编写代码时,复制了X轴刻度的代码模式来修改为Y轴刻度,但在修改参数时不小心将两个独立的参数用括号包裹成了一个元组,导致`int()`函数接收到两个参数而抛出异常。

### 类似的代码
第186行的X轴刻度代码是正确的:
```python
painter.drawLine(int(p.x()), int(origin_screen.y()), int(p.x()), int(origin_screen.y() + 5))
```

第193行的Y轴刻度代码应该是类似的,但括号位置错误:
```python
# 错误
painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5, int(p.y())))
# 应该是
painter.drawLine(int(origin_screen.x()), int(p.y()), int(origin_screen.x() - 5), int(p.y()))
```

## 预防措施

### 代码审查建议
1. 仔细检查所有函数调用的参数列表
2. 确保括号位置正确
3. 使用IDE的语法检查功能
4. 运行前进行单元测试

### 测试建议
1. 添加可视化组件的单元测试
2. 测试所有绘图方法
3. 边界条件测试
4. 参数验证测试

## 版本信息

- **Bug发现版本**: v2.2 (初始发布)
- **Bug修复版本**: v2.2.1 (热修复)
- **修复日期**: 2025-04-01
- **修复类型**: 语法错误
- **测试状态**: ✅ 已验证

## 相关文档

- **开发文档**: FINE_MAP_REVISION_TEST_REPORT.md
- **用户指南**: FINE_MAP_REVISION_USER_GUIDE.md
- **代码位置**: ui_fine_map_revision.py:193

## 总结

这是一个简单的语法错误,由于括号位置不当导致`int()`函数接收到错误的参数数量。修复非常简单,只需要调整括号位置即可。修复后程序运行正常,所有可视化功能正常工作。

---

**修复状态**: ✅ 完成
**验证状态**: ✅ 通过
**影响**: 小范围,已修复
