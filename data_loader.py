"""
数据加载和处理模块
"""
import json
import csv
from typing import List, Dict, Tuple
from pathlib import Path

class DataLoader:
    """
    数据加载器，支持多种格式的GT和预测数据
    """
    
    @staticmethod
    def load_gt_annotations(file_path: str) -> List[Dict]:
        """
        加载GT标注数据
        支持格式：JSON、CSV
        期望格式：[{start_time: float, end_time: float, label: str}, ...]
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            return DataLoader._load_json_annotations(file_path)
        elif file_path.suffix.lower() == '.csv':
            return DataLoader._load_csv_annotations(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
    
    @staticmethod
    def load_prediction_results(file_path: str) -> List[Dict]:
        """
        加载预测结果数据
        期望格式：[{start_time: float, end_time: float, predictions: [{label: str, confidence: float}, ...]}, ...]
        """
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            return DataLoader._load_json_predictions(file_path)
        elif file_path.suffix.lower() == '.csv':
            return DataLoader._load_csv_predictions(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")
    
    @staticmethod
    def _load_json_annotations(file_path: Path) -> List[Dict]:
        """
        加载JSON格式的标注数据
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 确保数据格式正确
        annotations = []
        for item in data:
            annotations.append({
                'start_time': float(item['start_time']),
                'end_time': float(item['end_time']),
                'label': str(item['label'])
            })
        
        # 按开始时间排序
        annotations.sort(key=lambda x: x['start_time'])
        return annotations
    
    @staticmethod
    def _load_csv_annotations(file_path: Path) -> List[Dict]:
        """
        加载CSV格式的标注数据
        期望列：start_time, end_time, label
        """
        annotations = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                annotations.append({
                    'start_time': float(row['start_time']),
                    'end_time': float(row['end_time']),
                    'label': str(row['label'])
                })
        
        # 按开始时间排序
        annotations.sort(key=lambda x: x['start_time'])
        return annotations
    
    @staticmethod
    def _load_json_predictions(file_path: Path) -> List[Dict]:
        """
        加载JSON格式的预测结果
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        predictions = []
        for item in data:
            # 确保预测结果按置信度排序
            pred_list = item.get('predictions', [])
            pred_list.sort(key=lambda x: x['confidence'], reverse=True)
            
            predictions.append({
                'start_time': float(item['start_time']),
                'end_time': float(item['end_time']),
                'predictions': pred_list
            })
        
        # 按开始时间排序
        predictions.sort(key=lambda x: x['start_time'])
        return predictions
    
    @staticmethod
    def _load_csv_predictions(file_path: Path) -> List[Dict]:
        """
        加载CSV格式的预测结果
        期望列：start_time, end_time, label_1, conf_1, label_2, conf_2, ...
        """
        predictions = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                start_time = float(row['start_time'])
                end_time = float(row['end_time'])
                
                # 提取预测结果
                pred_list = []
                i = 1
                while f'label_{i}' in row and f'conf_{i}' in row:
                    if row[f'label_{i}'] and row[f'conf_{i}']:
                        pred_list.append({
                            'label': str(row[f'label_{i}']),
                            'confidence': float(row[f'conf_{i}'])
                        })
                    i += 1
                
                # 按置信度排序
                pred_list.sort(key=lambda x: x['confidence'], reverse=True)
                
                predictions.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'predictions': pred_list
                })
        
        # 按开始时间排序
        predictions.sort(key=lambda x: x['start_time'])
        return predictions
    
    @staticmethod
    def create_sample_data(output_dir: str = '.'):
        """
        创建示例数据文件，用于测试
        """
        output_dir = Path(output_dir)
        
        # 创建示例GT数据
        gt_data = [
            {'start_time': 0.0, 'end_time': 5.0, 'label': 'Kick-off'},
            {'start_time': 5.0, 'end_time': 12.0, 'label': 'Foul'},
            {'start_time': 12.0, 'end_time': 20.0, 'label': 'Direct free-kick'},
            {'start_time': 20.0, 'end_time': 30.0, 'label': 'Background'},
            {'start_time': 30.0, 'end_time': 35.0, 'label': 'Shots on target'},
            {'start_time': 35.0, 'end_time': 38.0, 'label': 'Goal'},
        ]
        
        with open(output_dir / 'sample_gt.json', 'w', encoding='utf-8') as f:
            json.dump(gt_data, f, indent=2, ensure_ascii=False)
        
        # 创建示例预测数据（5秒窗口，2.5秒步长）
        pred_data = []
        import random
        
        labels = ['Background', 'Red card', 'Indirect free-kick', 'Throw-in', 'Yellow card', 'Corner', 'Clearance', 'Goal']
        
        for i in range(0, 40, 3):  # 每2.5秒一个窗口，简化为3秒
            start_time = float(i)
            end_time = start_time + 5.0
            
            # 生成Top-5预测
            predictions = []
            remaining_conf = 1.0
            
            for j in range(5):
                if j == 4:
                    conf = remaining_conf
                else:
                    conf = random.uniform(0.05, remaining_conf * 0.6)
                    remaining_conf -= conf
                
                predictions.append({
                    'label': random.choice(labels),
                    'confidence': round(conf, 3)
                })
            
            # 按置信度排序
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            pred_data.append({
                'start_time': start_time,
                'end_time': end_time,
                'predictions': predictions
            })
        
        with open(output_dir / 'sample_predictions.json', 'w', encoding='utf-8') as f:
            json.dump(pred_data, f, indent=2, ensure_ascii=False)
        
        print(f"示例数据已创建：")
        print(f"  GT数据: {output_dir / 'sample_gt.json'}")
        print(f"  预测数据: {output_dir / 'sample_predictions.json'}")

if __name__ == "__main__":
    # 创建示例数据
    DataLoader.create_sample_data() 