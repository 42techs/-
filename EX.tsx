import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, MessageSquare, Hash, Users, Clock, Brain, Heart, AlertCircle } from 'lucide-react';

const NLPAnalysisShowcase = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // 模拟数据
  const wordFrequencyData = [
    { word: '人工智能', count: 245 },
    { word: '深度学习', count: 189 },
    { word: '机器学习', count: 156 },
    { word: '神经网络', count: 134 },
    { word: '数据分析', count: 98 }
  ];

  const sentimentData = [
    { name: '积极', value: 456, color: '#10b981' },
    { name: '中性', value: 234, color: '#6b7280' },
    { name: '消极', value: 89, color: '#ef4444' }
  ];

  const sentimentDistribution = [
    { category: '非常消极', count: 23 },
    { category: '消极', count: 66 },
    { category: '中性', count: 234 },
    { category: '积极', count: 312 },
    { category: '非常积极', count: 144 }
  ];

  const temporalData = [
    { date: '01-05', count: 145 },
    { date: '01-06', count: 189 },
    { date: '01-07', count: 234 },
    { date: '01-08', count: 267 },
    { date: '01-09', count: 298 },
    { date: '01-10', count: 321 },
    { date: '01-11', count: 356 }
  ];

  const hotTopics = [
    { hashtag: '#AI技术发展', count: 1234 },
    { hashtag: '#机器学习应用', count: 987 },
    { hashtag: '#数据科学', count: 756 },
    { hashtag: '#深度学习', count: 654 }
  ];

  const topicModeling = [
    { 
      id: 1, 
      name: '技术创新',
      keywords: ['人工智能', '深度学习', '算法', '创新', '技术']
    },
    { 
      id: 2, 
      name: '行业应用',
      keywords: ['应用', '场景', '解决方案', '实践', '案例']
    },
    { 
      id: 3, 
      name: '数据分析',
      keywords: ['数据', '分析', '模型', '预测', '可视化']
    }
  ];

  const hotContents = [
    { 
      text: 'AI技术在医疗领域的突破性进展...',
      heat: 8956,
      reposts: 2341,
      comments: 1234,
      likes: 5381
    },
    { 
      text: '深度学习模型优化的最新研究成果...',
      heat: 7234,
      reposts: 1876,
      comments: 987,
      likes: 4371
    }
  ];

  const analysisModules = [
    {
      id: 'word',
      name: '词频分析',
      icon: <Hash className="w-5 h-5" />,
      description: '提取高频词、TF-IDF关键词、TextRank关键词',
      outputs: ['词频统计表', '关键词列表', '词汇多样性指标']
    },
    {
      id: 'sentiment',
      name: '情感分析',
      icon: <Heart className="w-5 h-5" />,
      description: '基于SnowNLP的情感倾向分析',
      outputs: ['情感分数', '情感分类（积极/中性/消极）', '情感强度', '情感分布统计']
    },
    {
      id: 'topic',
      name: '主题建模',
      icon: <Brain className="w-5 h-5" />,
      description: 'LDA主题模型提取文本主题',
      outputs: ['主题列表', '主题关键词', '文档-主题分布', '主题一致性分数']
    },
    {
      id: 'temporal',
      name: '时间序列',
      icon: <Clock className="w-5 h-5" />,
      description: '分析数据的时间趋势和活跃时段',
      outputs: ['每日分布', '每小时分布', '星期分布', '趋势方向', '高峰时段']
    },
    {
      id: 'hotspot',
      name: '热点分析',
      icon: <TrendingUp className="w-5 h-5" />,
      description: '识别热门话题、用户和内容',
      outputs: ['热门话题标签', '热门@用户', '热门内容排行', '传播分析统计']
    },
    {
      id: 'viz',
      name: '可视化图表',
      icon: <MessageSquare className="w-5 h-5" />,
      description: '基于ECharts的数据可视化',
      outputs: ['词云图', '情感饼图', '时间折线图', '词频柱状图', '散点图']
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            社交媒体NLP分析系统
          </h1>
          <p className="text-gray-600">基于Python的综合文本分析平台产出展示</p>
        </div>

        {/* 标签导航 */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'overview' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            功能模块
          </button>
          <button
            onClick={() => setActiveTab('word')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'word' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            词频分析
          </button>
          <button
            onClick={() => setActiveTab('sentiment')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'sentiment' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            情感分析
          </button>
          <button
            onClick={() => setActiveTab('temporal')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'temporal' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            时间趋势
          </button>
          <button
            onClick={() => setActiveTab('hotspot')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'hotspot' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            热点分析
          </button>
          <button
            onClick={() => setActiveTab('topic')}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors ${
              activeTab === 'topic' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            主题建模
          </button>
        </div>

        {/* 内容区域 */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          {/* 功能模块概览 */}
          {activeTab === 'overview' && (
            <div>
              <h2 className="text-2xl font-bold mb-6 text-gray-900">系统功能模块</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisModules.map((module) => (
                  <div key={module.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                        {module.icon}
                      </div>
                      <h3 className="font-semibold text-lg">{module.name}</h3>
                    </div>
                    <p className="text-gray-600 text-sm mb-3">{module.description}</p>
                    <div className="space-y-1">
                      <p className="text-xs font-medium text-gray-500">产出内容：</p>
                      {module.outputs.map((output, idx) => (
                        <div key={idx} className="flex items-start gap-2">
                          <div className="w-1 h-1 rounded-full bg-blue-500 mt-1.5"></div>
                          <span className="text-sm text-gray-700">{output}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex gap-2 items-start">
                  <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-blue-900 mb-2">核心特点</h4>
                    <ul className="text-sm text-blue-800 space-y-1">
                      <li>• 支持微博文章和评论数据的综合分析</li>
                      <li>• 一次性返回所有分析结果（综合分析API）</li>
                      <li>• 基于jieba分词、SnowNLP情感分析、sklearn的LDA主题模型</li>
                      <li>• 提供ECharts可视化图表配置</li>
                      <li>• 支持自定义停用词、时间范围筛选（1-90天）</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 词频分析 */}
          {activeTab === 'word' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">词频分析结果</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-4">高频词TOP5</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={wordFrequencyData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="word" type="category" width={80} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">统计指标</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 bg-gray-50 rounded">
                      <span className="text-gray-600">总词数</span>
                      <span className="font-semibold">15,234</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded">
                      <span className="text-gray-600">唯一词数</span>
                      <span className="font-semibold">3,456</span>
                    </div>
                    <div className="flex justify-between p-3 bg-gray-50 rounded">
                      <span className="text-gray-600">词汇多样性</span>
                      <span className="font-semibold">0.2269</span>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-blue-50 rounded text-sm">
                    <p className="text-blue-800">
                      <strong>产出：</strong>包括词频统计、TF-IDF关键词、TextRank关键词三种提取方式
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 情感分析 */}
          {activeTab === 'sentiment' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">情感分析结果</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-4">情感分布（三分类）</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={sentimentData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {sentimentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">细粒度情感分布</h3>
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={sentimentDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" angle={-15} textAnchor="end" height={60} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="mt-6 grid md:grid-cols-3 gap-4">
                <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                  <div className="text-sm text-green-600 mb-1">平均情感分数</div>
                  <div className="text-2xl font-bold text-green-700">0.6234</div>
                </div>
                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                  <div className="text-sm text-blue-600 mb-1">中位数</div>
                  <div className="text-2xl font-bold text-blue-700">0.5891</div>
                </div>
                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                  <div className="text-sm text-purple-600 mb-1">标准差</div>
                  <div className="text-2xl font-bold text-purple-700">0.1876</div>
                </div>
              </div>
            </div>
          )}

          {/* 时间趋势 */}
          {activeTab === 'temporal' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">时间序列分析</h2>
              <div className="mb-6">
                <h3 className="font-semibold mb-4">每日发布量趋势</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={temporalData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-3">趋势分析</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">趋势方向</span>
                      <span className="font-semibold text-green-600">↗ 增长中</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">统计天数</span>
                      <span className="font-semibold">7天</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">日均发布量</span>
                      <span className="font-semibold">258.6</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-3">高峰时段</h4>
                  <div className="space-y-2">
                    <div className="px-3 py-2 bg-blue-50 rounded text-sm">2026-01-10 18:00 (热度最高)</div>
                    <div className="px-3 py-2 bg-blue-50 rounded text-sm">2026-01-10 12:00</div>
                    <div className="px-3 py-2 bg-blue-50 rounded text-sm">2026-01-09 20:00</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 热点分析 */}
          {activeTab === 'hotspot' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">热点话题与内容</h2>
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h3 className="font-semibold mb-4">热门话题标签</h3>
                  <div className="space-y-2">
                    {hotTopics.map((topic, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <span className="text-blue-600 font-medium">{topic.hashtag}</span>
                        <span className="text-sm text-gray-500">{topic.count.toLocaleString()} 次</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold mb-4">传播统计</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-gradient-to-r from-red-50 to-pink-50 rounded-lg">
                      <div className="text-sm text-red-600 mb-1">总互动量</div>
                      <div className="text-2xl font-bold text-red-700">125,678</div>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <div className="p-3 bg-gray-50 rounded text-center">
                        <div className="text-xs text-gray-500">转发</div>
                        <div className="font-semibold">34,567</div>
                      </div>
                      <div className="p-3 bg-gray-50 rounded text-center">
                        <div className="text-xs text-gray-500">评论</div>
                        <div className="font-semibold">28,934</div>
                      </div>
                      <div className="p-3 bg-gray-50 rounded text-center">
                        <div className="text-xs text-gray-500">点赞</div>
                        <div className="font-semibold">62,177</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-4">热门内容TOP2</h3>
                {hotContents.map((content, idx) => (
                  <div key={idx} className="mb-3 p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <p className="text-gray-700 mb-3">{content.text}</p>
                    <div className="flex gap-4 text-sm text-gray-500">
                      <span>🔥 热度: {content.heat.toLocaleString()}</span>
                      <span>🔄 转发: {content.reposts.toLocaleString()}</span>
                      <span>💬 评论: {content.comments.toLocaleString()}</span>
                      <span>❤️ 点赞: {content.likes.toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 主题建模 */}
          {activeTab === 'topic' && (
            <div>
              <h2 className="text-2xl font-bold mb-6">主题建模结果（LDA）</h2>
              <div className="grid gap-4 mb-6">
                {topicModeling.map((topic) => (
                  <div key={topic.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-lg text-blue-700">
                        主题 {topic.id}: {topic.name}
                      </h3>
                      <span className="text-sm text-gray-500">一致性: 0.87</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {topic.keywords.map((keyword, idx) => (
                        <span 
                          key={idx} 
                          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <h4 className="font-semibold text-purple-900 mb-2">模型参数</h4>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-purple-600">主题数量:</span>
                    <span className="ml-2 font-semibold">3</span>
                  </div>
                  <div>
                    <span className="text-purple-600">困惑度:</span>
                    <span className="ml-2 font-semibold">245.67</span>
                  </div>
                  <div>
                    <span className="text-purple-600">迭代次数:</span>
                    <span className="ml-2 font-semibold">20</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* API说明 */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">API接口说明</h3>
          <div className="space-y-3 text-sm">
            <div className="p-3 bg-gray-50 rounded">
              <code className="text-blue-600">GET /api/analysis/comprehensive</code>
              <p className="text-gray-600 mt-1">综合分析接口 - 一次性返回所有分析结果（参数: type, days, article_id）</p>
            </div>
            <div className="p-3 bg-gray-50 rounded">
              <code className="text-blue-600">POST /api/analysis/charts/*</code>
              <p className="text-gray-600 mt-1">图表生成接口 - 生成词云、饼图、折线图等ECharts配置</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NLPAnalysisShowcase;