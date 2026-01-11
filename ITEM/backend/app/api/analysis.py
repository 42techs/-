from flask import Blueprint, request
from app.services.npl.nlp_service_manager import NLPServiceManager
from app.services.visualization.echarts_service import EchartsService
from app.utils.jwt_auth import token_required
from app.utils.responses import api_ok, api_error
import logging
import traceback

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

# 全局服务实例
_nlp_manager = None
_echarts_service = EchartsService()


def get_nlp_manager():
    """获取NLP管理器"""
    global _nlp_manager
    if _nlp_manager is None:
        from flask import current_app
        _nlp_manager = NLPServiceManager(
            mongo_uri=current_app.config['MONGO_URI'],
            database=current_app.config['MONGO_DATABASE']
        )
    return _nlp_manager


@analysis_bp.route('/comprehensive', methods=['GET'])
@token_required
def comprehensive_analysis():
    """综合分析接口 - 一次性返回所有分析结果"""
    try:
        manager = get_nlp_manager()
        
        data_type = request.args.get('type', 'articles')
        days = request.args.get('days', 7, type=int)
        article_id = request.args.get('article_id')
        
        logger.info(f"接收到分析请求: type={data_type}, days={days}, article_id={article_id}")
        
        # 参数验证
        if data_type not in ['articles', 'comments']:
            logger.warning(f"无效的数据类型: {data_type}")
            return api_error('类型必须是articles或comments')
        
        if not 1 <= days <= 90:
            logger.warning(f"无效的天数: {days}")
            return api_error('时间范围必须在1-90天之间')
        
        # 执行分析
        logger.info("开始执行分析...")
        result = manager.comprehensive_analysis(data_type, days, article_id)
        
        # 🔧 关键修复：检查返回结果的结构
        logger.info(f"分析结果结构: success={result.get('success')}, keys={result.keys()}")
        
        if not result:
            logger.error("分析结果为空")
            return api_error('分析失败：返回结果为空')
        
        if not result.get('success'):
            error_msg = result.get('message', '分析失败')
            logger.error(f"分析失败: {error_msg}")
            return api_error(error_msg)
        
        response_data = {
            'total_items': result.get('total_items', 0),
            'analysis_timestamp': result.get('analysis_timestamp'),
            'data_type': result.get('data_type'),
            'time_range_days': result.get('time_range_days'),
            'word_analysis': result.get('word_analysis', {}),
            'sentiment_analysis': result.get('sentiment_analysis', {}),
            'topic_analysis': result.get('topic_analysis', {}),
            'temporal_analysis': result.get('temporal_analysis', {}),
            'hotspot_analysis': result.get('hotspot_analysis', {})
        }
        
        logger.info("分析完成，返回结果")
        return api_ok(data=response_data, message='综合分析完成')
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"综合分析异常: {e}")
        logger.error(f"异常堆栈: {error_trace}")
        return api_error(f'分析失败: {str(e)}', status_code=500)


@analysis_bp.route('/charts/word-cloud', methods=['POST'])
@token_required
def generate_word_cloud_chart():
    """生成词云图表配置"""
    try:
        data = request.get_json()
        word_data = data.get('word_data', [])
        
        if not word_data:
            return api_error('缺少词云数据')
        
        chart_options = _echarts_service.generate_word_cloud(word_data)
        
        return api_ok(data={'chart_options': chart_options}, message='词云图表生成成功')
        
    except Exception as e:
        logger.error(f"词云生成失败: {e}")
        return api_error(f'生成失败: {str(e)}', status_code=500)


@analysis_bp.route('/charts/sentiment-pie', methods=['POST'])
@token_required
def generate_sentiment_pie_chart():
    """生成情感饼图配置"""
    try:
        data = request.get_json()
        sentiment_stats = data.get('sentiment_stats', {})
        
        chart_options = _echarts_service.generate_sentiment_pie(sentiment_stats)
        
        return api_ok(data={'chart_options': chart_options}, message='情感饼图生成成功')
        
    except Exception as e:
        logger.error(f"饼图生成失败: {e}")
        return api_error(f'生成失败: {str(e)}', status_code=500)


@analysis_bp.route('/charts/temporal-line', methods=['POST'])
@token_required
def generate_temporal_line_chart():
    """生成时间趋势图配置"""
    try:
        data = request.get_json()
        daily_data = data.get('daily_data', [])
        
        chart_options = _echarts_service.generate_temporal_line(daily_data)
        
        return api_ok(data={'chart_options': chart_options}, message='时间趋势图生成成功')
        
    except Exception as e:
        logger.error(f"趋势图生成失败: {e}")
        return api_error(f'生成失败: {str(e)}', status_code=500)