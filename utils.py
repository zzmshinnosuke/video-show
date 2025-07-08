"""
工具函数和配置
"""
import numpy as np
from typing import Dict, List, Tuple
import matplotlib.colors as mcolors

# 颜色配置 - 18类足球动作的颜色映射
COLOR_MAP = {
    'Background': '#D3D3D3',           # 浅灰色 - 背景
    'Red card': '#8B0000',             # 深红色 - 红牌
    'Indirect free-kick': '#90EE90',   # 浅绿色 - 间接任意球
    'Throw-in': '#20B2AA',             # 浅海绿 - 界外球
    'Yellow card': '#FFD700',          # 黄色 - 黄牌
    'Corner': '#00BFFF',               # 深天蓝 - 角球
    'Clearance': '#9932CC',            # 暗兰花紫 - 解围
    'Ball out of play': '#696969',     # 暗灰色 - 球出界
    'Shots on target': '#DC143C',      # 猩红色 - 射正
    'Shots off target': '#F08080',     # 浅珊瑚色 - 射偏
    'Substitution': '#FFA500',         # 橙色 - 换人
    'Foul': '#FF4500',                 # 橙红色 - 犯规
    'Penalty': '#800080',              # 紫色 - 点球
    'Direct free-kick': '#32CD32',     # 酸橙绿 - 直接任意球
    'Kick-off': '#4682B4',             # 钢蓝色 - 开球
    'Goal': '#FF0000',                 # 红色 - 进球
    'Yellow->red card': '#FF8C00',     # 深橙色 - 黄转红牌
    'Offside': '#FF69B4'               # 粉色 - 越位
}

def get_color_rgba(label: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
    """
    获取标签对应的RGBA颜色
    """
    hex_color = COLOR_MAP.get(label, COLOR_MAP['Background'])
    rgb = mcolors.hex2color(hex_color)
    rgba = tuple(int(c * 255) for c in rgb) + (int(alpha * 255),)
    return rgba

def format_time(seconds: float) -> str:
    """
    将秒数格式化为 MM:SS 格式
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def find_current_annotations(annotations: List[Dict], current_time: float) -> List[Dict]:
    """
    查找当前时间对应的标注
    """
    current_annotations = []
    for ann in annotations:
        if ann['start_time'] <= current_time <= ann['end_time']:
            current_annotations.append(ann)
    return current_annotations

def calculate_window_predictions(predictions: List[Dict], current_time: float, window_size: float = 5.0) -> List[Dict]:
    """
    计算当前时间窗口的预测结果
    窗口大小5秒，步长2.5秒
    """
    # 找到覆盖当前时间的所有窗口
    relevant_windows = []
    for pred in predictions:
        window_start = pred['start_time']
        window_end = pred['end_time']
        if window_start <= current_time <= window_end:
            relevant_windows.append(pred)
    
    return relevant_windows

def get_confusion_matrix_color(gt_label: str, pred_label: str) -> str:
    """
    根据GT和预测标签返回适当的颜色
    """
    if gt_label == pred_label:
        return '#00FF00'  # 绿色表示正确
    else:
        return '#FF0000'  # 红色表示错误

class WindowManager:
    """
    滑动窗口管理器
    """
    def __init__(self, window_size: float = 5.0, step_size: float = 2.5):
        self.window_size = window_size
        self.step_size = step_size
    
    def get_window_index(self, time: float) -> int:
        """
        根据时间获取窗口索引
        """
        return int(time / self.step_size)
    
    def get_window_time_range(self, index: int) -> Tuple[float, float]:
        """
        根据窗口索引获取时间范围
        """
        start_time = index * self.step_size
        end_time = start_time + self.window_size
        return start_time, end_time
    
    def get_overlapping_windows(self, time: float) -> List[int]:
        """
        获取覆盖指定时间的所有窗口索引
        """
        overlapping_windows = []
        # 向前查找可能的窗口
        for i in range(max(0, int((time - self.window_size) / self.step_size)), 
                      int(time / self.step_size) + 2):
            start_time, end_time = self.get_window_time_range(i)
            if start_time <= time <= end_time:
                overlapping_windows.append(i)
        return overlapping_windows 