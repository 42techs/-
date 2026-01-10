"""PyEcharts可视化服务"""
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, WordCloud, Scatter, Calendar, Graph
from typing import Dict, List
import json

class EchartsService:
    """PyEcharts图表生成服务"""
    
    @staticmethod
    def generate_word_cloud(word_data: List[Dict]) -> str:
        """生成词云图配置"""
        data = [(item['word'], item['count']) for item in word_data]
        
        chart = (
            WordCloud()
            .add("", data, word_size_range=[20, 100], shape='circle')
            .set_global_opts(
                title_opts=opts.TitleOpts(title="词云分析"),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )
        
        return chart.dump_options_with_quotes()
    
    @staticmethod
    def generate_sentiment_pie(sentiment_stats: Dict) -> str:
        """生成情感分布饼图"""
        data = [
            ("积极", sentiment_stats.get('positive_count', 0)),
            ("中性", sentiment_stats.get('neutral_count', 0)),
            ("消极", sentiment_stats.get('negative_count', 0))
        ]
        
        chart = (
            Pie()
            .add("", data, radius=["40%", "75%"])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="情感分布"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_left="left")
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
        )
        
        return chart.dump_options_with_quotes()
    
    @staticmethod
    def generate_temporal_line(daily_data: List[Dict]) -> str:
        """生成时间趋势折线图"""
        dates = [item['date'] for item in daily_data]
        counts = [item['count'] for item in daily_data]
        
        chart = (
            Line()
            .add_xaxis(dates)
            .add_yaxis("数量", counts, is_smooth=True)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="时间趋势分析"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)]
            )
        )
        
        return chart.dump_options_with_quotes()
    
    @staticmethod
    def generate_word_frequency_bar(word_freq: List[Dict], top_n: int = 20) -> str:
        """生成词频柱状图"""
        words = [item['word'] for item in word_freq[:top_n]]
        counts = [item['count'] for item in word_freq[:top_n]]
        
        chart = (
            Bar()
            .add_xaxis(words)
            .add_yaxis("词频", counts)
            .reversal_axis()  # 横向柱状图
            .set_global_opts(
                title_opts=opts.TitleOpts(title="高频词统计"),
                xaxis_opts=opts.AxisOpts(name="频次"),            
                yaxis_opts=opts.AxisOpts(name="词语")
        )
        )
        return chart.dump_options_with_quotes()

    @staticmethod
    def generate_sentiment_distribution_bar(distribution: Dict) -> str:
        """生成情感分布柱状图"""
        categories = ['非常消极', '消极', '中性', '积极', '非常积极']
        values = [
            distribution.get('very_negative', 0),
            distribution.get('negative', 0),
            distribution.get('neutral', 0),
            distribution.get('positive', 0),
            distribution.get('very_positive', 0)
        ]
    
        chart = (
            Bar()
            .add_xaxis(categories)
            .add_yaxis("数量", values)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="情感分布详情"),
                xaxis_opts=opts.AxisOpts(name="情感类别"),
                yaxis_opts=opts.AxisOpts(name="数量")
            )   
        )
    
        return chart.dump_options_with_quotes()

    @staticmethod
    def generate_hotspot_scatter(hot_contents: List[Dict]) -> str:
        """生成热点内容散点图"""
        data = [
            [item['comments'], item['reposts'], item['likes'], item['text_preview'][:30]]
            for item in hot_contents[:50]
        ]
    
        chart = (
            Scatter()
            .add_xaxis([d[0] for d in data])
            .add_yaxis(
                "热点内容",
                [{"value": [d[0], d[1]], "name": d[3]} for d in data],
                symbol_size=lambda x: x[1] / 10 + 5
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="热点内容分布"),
                xaxis_opts=opts.AxisOpts(name="评论数", type_="value"),
                yaxis_opts=opts.AxisOpts(name="转发数", type_="value"),
                tooltip_opts=opts.TooltipOpts(formatter="{c}")
            )
        )
    
        return chart.dump_options_with_quotes()