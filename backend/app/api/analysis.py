from flask import Blueprint, request, current_app
from app.services.analysis_service import AnalysisService
from app.utils.jwt_auth import token_required
from app.utils.responses import api_ok, api_error
import logging
from datetime import datetime

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

# 全局分析服务实例
_analysis_service = None


def get_analysis_service():
    """获取分析服务实例（单例模式）"""
    global _analysis_service
    if _analysis_service is None:
        try:
            _analysis_service = AnalysisService(
                mongo_uri=current_app.config['MONGO_URI'],
                database=current_app.config['MONGO_DATABASE']
            )
        except Exception as e:
            logger.error(f"分析服务初始化失败: {e}")
            return None
    return _analysis_service


@analysis_bp.route('/articles', methods=['GET'])
@token_required
def analyze_articles():
    """文章分析接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        days = request.args.get('days', default=7, type=int)
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        result = service.analyze_articles(days)
        
        if not result.get('success'):
            return api_error(result.get('message', '分析失败'))
        
        return api_ok(data=result, message='文章分析完成')
        
    except Exception as e:
        logger.error(f"文章分析接口错误: {e}")
        return api_error(f'分析处理失败: {str(e)}', status_code=500)


@analysis_bp.route('/comments', methods=['GET'])
@token_required
def analyze_comments():
    """评论分析接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        days = request.args.get('days', default=7, type=int)
        article_id = request.args.get('article_id', default=None, type=str)
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        result = service.analyze_comments(article_id, days)
        
        if not result.get('success'):
            return api_error(result.get('message', '分析失败'))
        
        return api_ok(data=result, message='评论分析完成')
        
    except Exception as e:
        logger.error(f"评论分析接口错误: {e}")
        return api_error(f'分析处理失败: {str(e)}', status_code=500)


@analysis_bp.route('/comparative', methods=['GET'])
@token_required
def comparative_analysis():
    """对比分析接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        days = request.args.get('days', default=7, type=int)
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        result = service.comparative_analysis(days)
        
        if not result.get('success'):
            return api_error(result.get('message', '分析失败'))
        
        return api_ok(data=result, message='对比分析完成')
        
    except Exception as e:
        logger.error(f"对比分析接口错误: {e}")
        return api_error(f'对比分析失败: {str(e)}', status_code=500)


@analysis_bp.route('/word-frequency', methods=['GET'])
@token_required
def get_word_frequency():
    """词频分析接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        analysis_type = request.args.get('type', default='articles', type=str)
        days = request.args.get('days', default=7, type=int)
        top_n = request.args.get('top_n', default=50, type=int)
        
        if analysis_type not in ['articles', 'comments']:
            return api_error('分析类型必须是articles或comments')
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        if top_n < 1 or top_n > 200:
            return api_error('top_n必须在1-200之间')
        
        # 获取数据
        if analysis_type == 'articles':
            data = service.get_articles_data(days)
            texts = [item.get('text_raw', '') for item in data]
        else:
            data = service.get_comments_data(None, days)
            texts = [item.get('text_raw', '') for item in data]
        
        if not texts:
            return api_error('没有找到可分析的数据')
        
        # 分词和词频统计
        words = service.segment_text(texts)
        word_freq = service.get_word_frequency(words, top_n)
        
        return api_ok(data={
            'analysis_type': analysis_type,
            'word_frequency': [{'word': w, 'count': c} for w, c in word_freq],
            'total_words': len(words),
            'unique_words': len(set(words)),
            'days': days
        }, message='词频分析完成')
        
    except Exception as e:
        logger.error(f"词频分析接口错误: {e}")
        return api_error(f'词频分析失败: {str(e)}', status_code=500)


@analysis_bp.route('/sentiment', methods=['GET'])
@token_required
def get_sentiment_analysis():
    """情感分析接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        analysis_type = request.args.get('type', default='articles', type=str)
        days = request.args.get('days', default=7, type=int)
        
        if analysis_type not in ['articles', 'comments']:
            return api_error('分析类型必须是articles或comments')
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        # 获取数据
        if analysis_type == 'articles':
            data = service.get_articles_data(days)
            texts = [item.get('text_raw', '') for item in data]
        else:
            data = service.get_comments_data(None, days)
            texts = [item.get('text_raw', '') for item in data]
        
        if not texts:
            return api_error('没有找到可分析的数据')
        
        # 情感分析
        sentiment_result = service.analyze_sentiment(texts)
        
        return api_ok(data={
            'analysis_type': analysis_type,
            'sentiment_analysis': sentiment_result,
            'total_texts_analyzed': len(texts),
            'days': days
        }, message='情感分析完成')
        
    except Exception as e:
        logger.error(f"情感分析接口错误: {e}")
        return api_error(f'情感分析失败: {str(e)}', status_code=500)


@analysis_bp.route('/word-cloud', methods=['GET'])
@token_required
def get_word_cloud_data():
    """词云数据接口"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        analysis_type = request.args.get('type', default='articles', type=str)
        days = request.args.get('days', default=7, type=int)
        
        if analysis_type not in ['articles', 'comments']:
            return api_error('分析类型必须是articles或comments')
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        # 获取数据
        if analysis_type == 'articles':
            data = service.get_articles_data(days)
            texts = [item.get('text_raw', '') for item in data]
        else:
            data = service.get_comments_data(None, days)
            texts = [item.get('text_raw', '') for item in data]
        
        if not texts:
            return api_error('没有找到可分析的数据')
        
        # 生成词云数据
        words = service.segment_text(texts)
        word_cloud_data = service.generate_word_cloud_data(words)
        
        if not word_cloud_data.get('success'):
            return api_error(word_cloud_data.get('message', '词云生成失败'))
        
        return api_ok(data=word_cloud_data, message='词云数据生成完成')
        
    except Exception as e:
        logger.error(f"词云数据接口错误: {e}")
        return api_error(f'词云数据生成失败: {str(e)}', status_code=500)


@analysis_bp.route('/stats', methods=['GET'])
@token_required
def get_analysis_stats():
    """获取分析统计信息"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        days = request.args.get('days', default=7, type=int)
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        # 获取基础统计
        articles = service.get_articles_data(days)
        comments = service.get_comments_data(None, days)
        
        stats = {
            'time_range_days': days,
            'total_articles': len(articles),
            'total_comments': len(comments),
            'articles_with_comments': len(set([c.get('article_id') for c in comments if c.get('article_id')])),
            'avg_comments_per_article': round(len(comments) / max(len(articles), 1), 2),
            'data_update_time': datetime.now().isoformat()
        }
        
        return api_ok(data={'statistics': stats}, message='统计信息获取成功')
        
    except Exception as e:
        logger.error(f"统计信息接口错误: {e}")
        return api_error(f'获取统计信息失败: {str(e)}', status_code=500)


@analysis_bp.route('/export', methods=['POST'])
@token_required
def export_analysis():
    """导出分析结果"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        data = request.get_json()
        if not data:
            return api_error('缺少请求数据')
        
        analysis_type = data.get('analysis_type')
        days = data.get('days', 7)
        format_type = data.get('format', 'json')
        
        if analysis_type not in ['articles', 'comments', 'comparative']:
            return api_error('不支持的分析类型')
        
        if days < 1 or days > 90:
            return api_error('时间范围必须在1-90天之间')
        
        # 根据类型执行分析
        if analysis_type == 'articles':
            result = service.analyze_articles(days)
        elif analysis_type == 'comments':
            result = service.analyze_comments(None, days)
        else:
            result = service.comparative_analysis(days)
        
        if not result.get('success'):
            return api_error(result.get('message', '分析失败'))
        
        # 导出结果
        export_result = service.export_analysis_results(result, format_type)
        
        if not export_result.get('success'):
            return api_error(export_result.get('message', '导出失败'))
        
        return api_ok(data=export_result, message='导出成功')
        
    except Exception as e:
        logger.error(f"导出接口错误: {e}")
        return api_error(f'导出失败: {str(e)}', status_code=500)


@analysis_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口（无需认证）"""
    try:
        service = get_analysis_service()
        if not service:
            return api_error('分析服务不可用', status_code=500)
        
        # 测试数据库连接
        articles_count = len(service.get_articles_data(1))
        
        return api_ok(data={
            'status': 'healthy',
            'database_connected': True,
            'articles_today': articles_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return api_error(f'健康检查失败: {str(e)}', status_code=500)