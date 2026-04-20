# Debug日志功能说明

## 概述

精细Map修订工具现在包含完整的debug日志输出功能,所有变量参数的改变都会实时输出到终端,便于后续测试和调试。

## 启用/禁用Debug模式

### 核心模块 (core_fine_map_revision.py)

在文件顶部有一个debug标志:

```python
# 调试标志
DEBUG_MODE = True
```

- `True`: 启用debug日志输出(默认)
- `False`: 禁用debug日志输出

### 修改方式

编辑 `D:\VScode_Project\Coordinate_Transform\core_fine_map_revision.py` 文件:

```python
# 禁用debug日志
DEBUG_MODE = False

# 或启用debug日志
DEBUG_MODE = True
```

## 日志格式

### 日志前缀

所有日志都带有明确的前缀标识:

- `[FineMap Core]` - 核心处理器日志
- `[Main Callback]` - 主程序回调函数日志

### 日志结构

```
============================================================
[前缀] 函数名() 开始执行
  参数1: 值1
  参数2: 值2
  ...
  处理过程信息
  ...
[前缀] 函数名() 成功完成
  结果信息
```

## 日志覆盖范围

### 1. 初始化日志

```
[FineMap Core] ============================================================
[FineMap Core] FineMapRevisionProcessor 初始化
[FineMap Core] 初始化完成
```

### 2. 导入CSV日志

```
============================================================
[FineMap Core] load_from_csv() 开始执行
参数: file_path = 'D:\path\to\file.csv'
CSV读取成功, 共 35171 行数据
检测到标准列名: X, Y
  读取点 0: (-70.0000, -70.0000)
  读取点 1: (-68.0000, -70.0000)
  读取点 2: (-66.0000, -70.0000)
_calculate_boundaries() 开始执行
  边界计算完成:
    X范围: [-70.0000, 70.0000]
    Y范围: [-70.0000, 70.0000]
    中心点: (0.0000, 0.0000)
    Pitch: x=2.0000, y=2.0000
✓ load_from_csv() 成功完成
  总点数: 35171
  X范围: [-70.0000, 70.0000]
  Y范围: [-70.0000, 70.0000]
  中心点: (0.0000, 0.0000)
```

### 3. 新建Map日志

```
============================================================
[FineMap Core] generate_rectangular_map() 开始执行
输入参数:
  x_length = 140.0000
  y_length = 140.0000
  x_pitch = 2.0000
  y_pitch = 2.0000
  center_x = 0.0000
  center_y = 0.0000
计算边界:
  x_min = -70.0000
  x_max = 70.0000
  y_min = -70.0000
  y_max = 70.0000
网格规模:
  num_x = 71
  num_y = 71
  预计总点数 = 5041
  生成点 0: (-70.0000, -70.0000)
  生成点 1: (-68.0000, -70.0000)
  生成点 2: (-66.0000, -70.0000)
✓ generate_rectangular_map() 成功完成
  实际生成点数: 5041
```

### 4. 主程序回调日志

```
[Main Callback] generate_fine_map() 调用
  参数: x_length=140.0000, y_length=140.0000
       x_pitch=2.0000, y_pitch=2.0000
       center=(0.0000, 0.0000)
[FineMap Core] generate_rectangular_map() 开始执行
...
[FineMap Core] generate_rectangular_map() 成功完成
[Main Callback] generate_fine_map() 返回: True
```

### 5. 编辑操作日志

#### 添加点
```

add_point() 执行
  添加点: (10.0000, 20.0000)
_calculate_boundaries() 开始执行
  边界计算完成:
    X范围: [-70.0000, 70.0000]
    Y范围: [-70.0000, 70.0000]
    中心点: (0.0234, 0.0123)
    Pitch: x=2.0000, y=2.0000
✓ 添加完成,当前总点数: 5042
[Main Callback] add_fine_map_point() 完成
```

#### 删除点
```

delete_point() 执行
  删除索引: 1000
✓ 删除成功: 删除了点 (-68.0000, -70.0000)
_calculate_boundaries() 开始执行
  边界计算完成:
    X范围: [-70.0000, 70.0000]
    Y范围: [-70.0000, 70.0000]
    中心点: (0.0000, 0.0000)
    Pitch: x=2.0000, y=2.0000
  剩余点数: 5041
[Main Callback] delete_fine_map_point() 返回: True
```

#### 更新点
```

update_point() 执行
  索引: 500
  新坐标: (5.5000, 10.5000)
✓ 更新成功:
    旧坐标: (-70.0000, -68.0000)
    新坐标: (5.5000, 10.5000)
_calculate_boundaries() 开始执行
  边界计算完成:
    X范围: [-70.0000, 70.0000]
    Y范围: [-70.0000, 70.0000]
    中心点: (0.0011, 0.0000)
    Pitch: x=2.0000, y=2.0000
[Main Callback] update_fine_map_point() 返回: True
```

### 6. 保存CSV日志

```

save_to_csv() 开始执行
  保存路径: 'D:\output.csv'
  小数位数: 6
  点数: 5041
  保存点 0: X=-70, Y=-70
  保存点 1: X=-68, Y=-70
  保存点 2: X=-66, Y=-70
✓ save_to_csv() 成功完成
  已保存 5041 行数据到 'D:\output.csv'
[Main Callback] save_fine_map_csv() 返回: True
```

## 完整的测试日志示例

### 场景: 创建并修改Map

```bash
$ python main.py

[FineMap Core] ============================================================
[FineMap Core] FineMapRevisionProcessor 初始化
[FineMap Core] 初始化完成

# 用户点击"新建Map"
[Main Callback] generate_fine_map() 调用
  参数: x_length=140.0000, y_length=140.0000
       x_pitch=2.0000, y_pitch=2.0000
       center=(0.0000, 0.0000)

[FineMap Core] ============================================================
[FineMap Core] generate_rectangular_map() 开始执行
输入参数:
  x_length = 140.0000
  y_length = 140.0000
  x_pitch = 2.0000
  y_pitch = 2.0000
  center_x = 0.0000
  center_y = 0.0000
计算边界:
  x_min = -70.0000
  x_max = 70.0000
  y_min = -70.0000
  y_max = 70.0000
网格规模:
  num_x = 71
  num_y = 71
  预计总点数 = 5041
  生成点 0: (-70.0000, -70.0000)
  生成点 1: (-68.0000, -70.0000)
  生成点 2: (-66.0000, -70.0000)
✓ generate_rectangular_map() 成功完成
  实际生成点数: 5041

[Main Callback] generate_fine_map() 返回: True

# 用户编辑点500
[Main Callback] update_fine_map_point() 调用
  索引: 500, 新坐标: (10.5000, 20.5000)

[FineMap Core]
update_point() 执行
  索引: 500
  新坐标: (10.5000, 20.5000)
✓ 更新成功:
    旧坐标: (-68.0000, -66.0000)
    新坐标: (10.5000, 20.5000)
_calculate_boundaries() 开始执行
  边界计算完成:
    X范围: [-70.0000, 70.0000]
    Y范围: [-70.0000, 70.0000]
    中心点: (0.0042, 0.0016)
    Pitch: x=2.0000, y=2.0000

[Main Callback] update_fine_map_point() 返回: True

# 用户保存CSV
[Main Callback] save_fine_map_csv() 调用
  保存路径: 'D:\test_output.csv'

[FineMap Core]
save_to_csv() 开始执行
  保存路径: 'D:\test_output.csv'
  小数位数: 6
  点数: 5041
  保存点 0: X=-70, Y=-70
  保存点 1: X=-68, Y=-70
  保存点 2: X=-66, Y=-70
✓ save_to_csv() 成功完成
  已保存 5041 行数据到 'D:\test_output.csv'

[Main Callback] save_fine_map_csv() 返回: True
```

## 日志查看方法

### 方法1: 终端直接查看
直接运行程序,所有日志会实时显示在终端:
```bash
cd D:\VScode_Project\Coordinate_Transform
python main.py
```

### 方法2: 重定向到文件
```bash
python main.py > debug_log.txt 2>&1
```

### 方法3: 使用PowerShell并保存
```powershell
python main.py | Tee-Object -FilePath debug_log.txt
```

### 方法4: 使用IDE运行
在PyCharm、VS Code等IDE中运行时,所有日志会显示在运行窗口中。

## 日志内容分析

### 关键信息点

1. **函数调用追踪**: 每个函数的开始和结束
2. **参数传递**: 所有输入参数的值
3. **中间状态**: 计算过程和中间结果
4. **最终结果**: 返回值和状态
5. **错误信息**: 失败原因和异常详情

### 调试技巧

1. **查找特定操作**: 搜索函数名,如 `load_from_csv`
2. **追踪数据流**: 从Main Callback到Core,看完整调用链
3. **验证参数**: 检查输入参数是否符合预期
4. **性能分析**: 查看操作耗时和点数
5. **错误定位**: 查看带有 `✗` 的失败日志

## 注意事项

1. **性能影响**: Debug模式会轻微影响性能,生产环境建议关闭
2. **日志量**: 大型Map(>10000点)会产生大量日志,建议重定向到文件
3. **敏感信息**: 日志包含完整文件路径,注意保密
4. **浮点精度**: 日志中浮点数显示4位小数,实际精度更高

## 版本信息

- **Debug版本**: v2.2
- **添加日期**: 2025-04-01
- **日志系统**: 完整覆盖所有核心操作

---

**提示**: 运行程序时保持终端窗口可见,所有操作都会实时显示debug日志!
