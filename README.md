# 视频分析可视化工具

这是一个专门用于可视化视频分析中Ground Truth和模型预测结果对比的工具。支持滑动窗口推理结果的实时显示。

## 功能特点

- **视频播放控制**: 支持播放、暂停、快进、快退、变速播放
- **实时分析面板**: 显示当前时间窗口的GT与Top-5预测结果对比
- **交互式时间轴**: 直观显示GT和预测结果的时间分布，支持点击跳转
- **类别过滤**: 可选择性显示特定类别
- **键盘快捷键**: 方便的播放控制
- **多格式支持**: 支持JSON和CSV格式的数据文件

## 界面布局

```
┌─────────────────────────────────┬──────────────────┐
│                                 │   实时分析面板   │
│         视频播放区域            │                  │
│                                 │  GT: FOUL ⚽     │
│                                 │  ──────────────  │
│                                 │  TOP-5 (conf) ↘  │
│                                 │  1. Tackle 0.61✗ │
│                                 │  2. Foul   0.27✓ │
│                                 │  3. Pass   0.05  │
│         (16:9 视频比例)         │  4. Clear  0.04  │
│                                 │  5. Offside 0.02 │
│                                 │                  │
│                                 │     时间轴       │
│─────────────────────────────────│  GT: ████████    │
│  [播放控制]  [进度条]  [速度]   │ Pred: ████████   │
└─────────────────────────────────┴──────────────────┘
```

## 安装与运行

### 1. 环境要求

- Python 3.8+
- PyQt6
- OpenCV
- 其他依赖见requirements.txt

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python video_analyzer.py
```

## 数据格式

### GT标注数据格式

**JSON格式** (`gt_annotations.json`):

```json
[
  {
    "start_time": 0.0,
    "end_time": 5.0,
    "label": "Kick-off"
  },
  {
    "start_time": 5.0,
    "end_time": 12.0,
    "label": "Foul"
  }
]
```

**CSV格式** (`gt_annotations.csv`):

```csv
start_time,end_time,label
0.0,5.0,Kick-off
5.0,12.0,Foul
12.0,20.0,Direct free-kick
```

### 预测结果数据格式

**JSON格式** (`predictions.json`):

```json
[
  {
    "start_time": 0.0,
    "end_time": 5.0,
    "predictions": [
      {"label": "Kick-off", "confidence": 0.85},
      {"label": "Foul", "confidence": 0.10},
      {"label": "Corner", "confidence": 0.03},
      {"label": "Shots on target", "confidence": 0.01},
      {"label": "Background", "confidence": 0.01}
    ]
  }
]
```

**CSV格式** (`predictions.csv`):

```csv
start_time,end_time,label_1,conf_1,label_2,conf_2,label_3,conf_3,label_4,conf_4,label_5,conf_5
0.0,5.0,Kick-off,0.85,Foul,0.10,Corner,0.03,Shots on target,0.01,Background,0.01
2.5,7.5,Foul,0.61,Corner,0.27,Kick-off,0.05,Clearance,0.04,Offside,0.02
```

## 使用步骤

1. **启动程序**: 运行 `python video_analyzer.py`
2. **加载视频**:

   - 点击"文件" → "打开视频"，选择MP4视频文件
   - 或使用工具栏的"打开视频"按钮
3. **加载数据**:

   - 点击"文件" → "加载GT数据"，选择GT标注文件
   - 点击"文件" → "加载预测数据"，选择预测结果文件
4. **开始分析**:

   - 点击播放按钮开始播放视频
   - 右侧面板会实时显示当前时间的GT和预测结果对比
   - 时间轴显示整个视频的标注分布
5. **交互操作**:

   - 点击时间轴可跳转到指定时间
   - 使用类别过滤可选择显示特定类别
   - 键盘快捷键控制播放
   - 调整"步长"设置来自定义逐帧控制的帧数（1-100帧）

## 键盘快捷键

| 快捷键 | 功能            |
| ------ | --------------- |
| 空格   | 播放/暂停       |
| ←     | 快退5秒         |
| →     | 快进5秒         |
| ,      | 后退指定帧数    |
| .      | 前进指定帧数    |
| Ctrl+O | 打开视频        |
| Ctrl+S | 停止播放        |
| Ctrl+Q | 退出程序        |

**注意**: 逐帧控制的步长可以在播放器界面中的"步长"设置中调整（1-100帧），设置会自动保存。

## 支持的类别

工具预定义了18种足球动作类别：

- Background (背景)
- Red card (红牌)
- Indirect free-kick (间接任意球)
- Throw-in (界外球)
- Yellow card (黄牌)
- Corner (角球)
- Clearance (解围)
- Ball out of play (球出界)
- Shots on target (射正)
- Shots off target (射偏)
- Substitution (换人)
- Foul (犯规)
- Penalty (点球)
- Direct free-kick (直接任意球)
- Kick-off (开球)
- Goal (进球)
- Yellow->red card (黄转红牌)
- Offside (越位)

每个类别都有对应的颜色编码，便于在时间轴上区分。

## 测试数据

程序提供了创建示例数据的功能：

1. 点击"文件" → "创建示例数据"
2. 程序会在当前目录生成 `sample_gt.json` 和 `sample_predictions.json`
3. 可以加载这些示例数据来测试工具功能

## 滑动窗口配置

- **窗口大小**: 5秒
- **步长**: 2.5秒
- **重叠**: 50%

这意味着每2.5秒会有一个新的预测窗口，每个窗口覆盖5秒的视频内容。

## 技术实现

- **GUI框架**: PyQt6
- **视频处理**: OpenCV
- **数据格式**: JSON/CSV
- **可视化**: 自定义绘制的时间轴和置信度条
- **设置保存**: QSettings (自动保存用户偏好设置)

## 故障排除

### 常见问题

1. **视频无法播放**

   - 检查视频文件格式是否支持
   - 确保OpenCV正确安装
2. **数据加载失败**

   - 检查JSON/CSV文件格式是否正确
   - 确认数据中的时间格式为浮点数
3. **程序崩溃**

   - 检查Python版本是否为3.8+
   - 确认所有依赖包已正确安装

### 性能优化

- 对于长视频，建议先加载较短片段进行测试
- 预测窗口数量过多时可能影响响应速度
- 可以通过类别过滤减少显示内容

## 许可证

此项目仅供学术研究和教育用途使用。

## 贡献

欢迎提交问题反馈和功能建议！
