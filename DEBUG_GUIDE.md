# Map建立工具 - 调试日志使用说明

## 📋 概述

已为Map建立工具添加完整的调试日志系统，所有用户操作和程序运行状态都会在终端中显示，便于问题诊断。

---

## 🐛 调试日志功能

### 1. UI层日志（ui_map_establish.py）

**日志内容：**
- ✅ 用户点击按钮事件
- ✅ 输入框的原始文本内容
- ✅ 文本类型和长度信息
- ✅ 数值转换过程（逐个参数）
- ✅ 参数验证结果
- ✅ 调用核心模块的参数传递
- ✅ 核心模块返回结果
- ✅ 异常详细信息（包括完整堆栈）

**日志示例：**
```
============================================================
[UI] 点击预览按钮
============================================================
[UI] 原始输入 - ref_x_text: '0' (type: str)
[UI] 原始输入 - ref_y_text: '0' (type: str)
[UI] 原始输入 - x_pitch_text: '2.00' (type: str)
[UI] 原始输入 - y_pitch_text: '2.00' (type: str)
[UI] 开始转换输入值为数字...
[UI] 晶圆尺寸: 8 inch
[UI] 转换成功 - ref_x: 0.0
[UI] 转换成功 - ref_y: 0.0
[UI] 转换成功 - x_pitch: 2.0
[UI] 转换成功 - y_pitch: 2.0
[UI] 起点位置: 左下
[UI] 扫描方向: X方向
[UI] 参数验证通过，调用核心处理模块...
```

### 2. 核心层日志（core_map_establish.py）

**日志内容：**
- ✅ 函数入口参数（包括类型）
- ✅ 网格点生成进度
- ✅ 边界计算结果
- ✅ 扫描路径生成过程
- ✅ 错误详情和堆栈信息

**日志示例：**
```
[CORE]
============================================================
[CORE] generate_map_data() 开始执行
[CORE] 完整参数列表:
[CORE]   ref_x: 0.0 (type: float)
[CORE]   ref_y: 0.0 (type: float)
[CORE]   x_pitch: 2.0 (type: float)
[CORE]   y_pitch: 2.0 (type: float)
[CORE]   wafer_size: 8 inch (type: str)
[CORE]   start_position: 左下 (type: str)
[CORE]   scan_direction: X方向 (type: str)
[CORE] 获取晶圆半径: 100.0mm
[CORE] 开始生成网格点...
[CORE] ==================================================
[CORE] generate_grid_points() 开始执行
[CORE] 输入参数 - ref_x: 0.0, ref_y: 0.0
[CORE] 输入参数 - x_pitch: 2.0, y_pitch: 2.0
[CORE] 输入参数 - radius: 100.0
[CORE] 计算网格范围 - x_range: 51, y_range: 51
[CORE] 检查了 10609 个点，保留 7825 个在圆内的点
[CORE] generate_grid_points() 执行完成
```

---

## 🔍 问题诊断流程

### 如果出现"请输入有效数字"错误：

#### 步骤1：查看UI日志
找到 `[UI] 原始输入` 相关日志，检查：
- 输入文本内容是否包含特殊字符
- 输入文本是否为空（只有空格）
- 是否有不可见字符

#### 步骤2：查看转换日志
找到 `[UI] 转换成功` 或 `[UI] 转换失败` 日志：
- 如果转换成功，会显示转换后的数值
- 如果转换失败，会显示具体的ValueError信息

#### 步骤3：查看完整堆栈
如果出现异常，日志会显示完整的Python堆栈跟踪，包括：
- 异常类型（ValueError、TypeError等）
- 异常信息
- 完整的函数调用链

---

## 📝 常见问题排查

### 问题1：输入框有默认值但仍然报错

**可能原因：**
- 输入框实际内容包含特殊字符（如全角数字、不可见字符）
- PyQt5输入控件返回的字符串格式异常

**排查方法：**
```
查看日志中的：
[UI] 原始输入 - x_pitch_text: '2.00' (type: str)
```
如果显示的内容与你看到的不一致，说明有特殊字符。

**解决方案：**
手动删除输入框内容，重新输入数字。

---

### 问题2：float转换失败

**可能原因：**
- 输入了全角数字（如２.００而非2.00）
- 输入了中文标点符号（如2.00而非2.00）
- 输入了科学计数法（如1e2）
- 包含空格或其他字符

**排查方法：**
```
查看日志中的：
[UI] 转换失败 - x_pitch_text: '２.００', 错误: could not convert string to float
```

**解决方案：**
确保使用半角数字（0-9）和小数点（.）

---

### 问题3：日志显示转换成功但仍然报错

**可能原因：**
- 核心模块处理逻辑出现异常
- 参数范围验证失败

**排查方法：**
查看 `[CORE]` 开头的日志，找到具体错误位置

---

## 🧪 测试调试功能

### 运行测试脚本：
```bash
python test_debug.py
```

**预期输出：**
- 显示完整的参数处理流程
- 显示生成的测量点数量
- 显示前10个点的坐标
- 无任何错误信息

---

## 💡 调试技巧

### 1. 启动程序时保留终端窗口

**Windows PowerShell:**
```powershell
python main.py
```
不要关闭窗口，所有日志会实时显示

### 2. 将日志输出到文件

**方法1：重定向**
```bash
python main.py > debug.log 2>&1
```

**方法2：修改代码**
在 `ui_map_establish.py` 和 `core_map_establish.py` 中添加：
```python
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)
```

### 3. 过滤特定日志

**只看UI层：**
```bash
python main.py | findstr "[UI]"
```

**只看核心层：**
```bash
python main.py | findstr "[CORE]"
```

**只看错误：**
```bash
python main.py | findstr /I "错误 error exception"
```

---

## 🔧 关闭调试日志

如果生产环境不需要日志，修改以下文件：

### ui_map_establish.py
注释掉所有 `print()` 语句（共约30处）

### core_map_establish.py
```python
# 修改调试标志
DEBUG_MODE = False  # 改为 False
```

---

## 📊 日志级别说明

| 日志类型 | 前缀 | 说明 |
|---------|------|------|
| 用户操作 | `[UI]` | 用户点击、输入等操作 |
| 核心处理 | `[CORE]` | 后台计算、数据处理 |
| 分隔线 | `=` | 标记重要操作的开始和结束 |
| 错误信息 | `错误/异常` | 问题诊断信息 |

---

## 🎯 完整示例：正常运行的日志

```
============================================================
[UI] 点击预览按钮
============================================================
[UI] 原始输入 - ref_x_text: '0' (type: str)
[UI] 原始输入 - ref_y_text: '0' (type: str)
[UI] 原始输入 - x_pitch_text: '2.00' (type: str)
[UI] 原始输入 - y_pitch_text: '2.00' (type: str)
[UI] 开始转换输入值为数字...
[UI] 晶圆尺寸: 8 inch
[UI] 转换成功 - ref_x: 0.0
[UI] 转换成功 - ref_y: 0.0
[UI] 转换成功 - x_pitch: 2.0
[UI] 转换成功 - y_pitch: 2.0
[UI] 起点位置: 左下
[UI] 扫描方向: X方向
[UI] 参数验证通过，调用核心处理模块...
[CORE]
============================================================
[CORE] generate_map_data() 开始执行
[CORE] 完整参数列表:
[CORE]   ref_x: 0.0 (type: float)
[CORE]   ref_y: 0.0 (type: float)
[CORE]   x_pitch: 2.0 (type: float)
[CORE]   y_pitch: 2.0 (type: float)
[CORE]   wafer_size: 8 inch (type: str)
[CORE]   start_position: 左下 (type: str)
[CORE]   scan_direction: X方向 (type: str)
[CORE] 获取晶圆半径: 100.0mm
[CORE] 开始生成网格点...
[CORE] generate_grid_points() 开始执行
[CORE] 输入参数 - ref_x: 0.0, ref_y: 0.0
[CORE] 输入参数 - x_pitch: 2.0, y_pitch: 2.0
[CORE] 输入参数 - radius: 100.0
[CORE] 计算网格范围 - x_range: 51, y_range: 51
[CORE] 检查了 10609 个点，保留 7825 个在圆内的点
[CORE] generate_grid_points() 执行完成
[CORE] 计算边界...
[CORE] 边界结果 - X: -98.00 ~ 98.00
[CORE] 边界结果 - Y: -98.00 ~ 98.00
[CORE] 生成扫描路径...
[CORE] 扫描路径生成完成，共 7825 个点
[CORE] generate_map_data() 执行成功
[CORE] ============================================================
[UI] 核心处理返回 - 总点数: 7825
[UI] 预览完成！
```

---

## 📞 问题报告

如果遇到问题，请提供：
1. 完整的终端日志输出
2. 使用的参数设置（截图或文字）
3. 具体的错误信息
4. 操作系统版本

---

**更新日期：** 2025-03-27
**版本：** v2.1 (with debug logging)
