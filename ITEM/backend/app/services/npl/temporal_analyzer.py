"""时间序列分析器"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict
import numpy as np
from .base_analyzer import BaseAnalyzer

class TemporalAnalyzer(BaseAnalyzer):
    """时间序列分析器 - 分析数据的时间趋势"""
    
    def analyze(self, data: List[Dict], date_field: str = 'created_at') -> Dict:
        """时间序列分析"""
        if not data:
            return self._empty_result()
        
        try:
            # 按时间聚合
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            weekday_counts = defaultdict(int)
            
            for item in data:
                if date_field not in item:
                    continue
                
                dt = item[date_field]
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                
                # 小时级别
                hour_key = dt.strftime('%Y-%m-%d %H:00')
                hourly_counts[hour_key] += 1
                
                # 天级别
                day_key = dt.strftime('%Y-%m-%d')
                daily_counts[day_key] += 1
                
                # 星期几
                weekday = dt.strftime('%A')
                weekday_counts[weekday] += 1
            
            # 计算趋势
            daily_series = sorted(daily_counts.items())
            trend = self._calculate_trend([count for _, count in daily_series])
            
            # 活跃时段分析
            hourly_series = sorted(hourly_counts.items())
            peak_hours = self._find_peak_hours(hourly_series)
            
            return {
                'daily_distribution': [
                    {'date': date, 'count': count}
                    for date, count in daily_series
                ],
                'hourly_distribution': [
                    {'hour': hour, 'count': count}
                    for hour, count in hourly_series[-24:]  # 最近24小时
                ],
                'weekday_distribution': [
                    {'weekday': day, 'count': count}
                    for day, count in sorted(weekday_counts.items())
                ],
                'trend_analysis': {
                    'trend_direction': trend,
                    'peak_hours': peak_hours,
                    'total_days': len(daily_counts),
                    'avg_daily_count': round(np.mean(list(daily_counts.values())), 2)
                }
            }
            
        except Exception as e:
            self.logger.error(f"时间序列分析失败: {e}")
            return self._empty_result()
    
    def _calculate_trend(self, values: List[int]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return 'stable'
        
        # 简单线性回归斜率
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _find_peak_hours(self, hourly_series: List[tuple]) -> List[str]:
        """找出活跃时段"""
        if not hourly_series:
            return []
        
        counts = [count for _, count in hourly_series]
        threshold = np.percentile(counts, 75) if counts else 0
        
        peak_hours = [
            hour for hour, count in hourly_series 
            if count >= threshold
        ]
        
        return peak_hours[:5]  # 返回前5个高峰时段
    
    def _empty_result(self) -> Dict:
        return {
            'daily_distribution': [],
            'hourly_distribution': [],
            'weekday_distribution': [],
            'trend_analysis': {}
        }