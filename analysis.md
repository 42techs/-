## 概述

本系统提供社交网络（微博）数据的多维度分析能力，包括：

* **词频分析** ：高频词、关键词提取
* **情感分析** ：情感倾向、情感强度、情感分布
* **主题分析** ：LDA主题建模
* **时间序列分析** ：趋势分析、活跃时段
* **热点分析** ：话题标签、热门内容、传播分析
* **可视化支持** ：ECharts图表配置生成

---

## 认证机制

所有接口均需要JWT认证，请在请求头中携带Token：

```http
Authorization: Bearer <your_jwt_token>
```

---

## 通用响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 失败响应

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

---

## 综合分析接口

### 1. 综合分析

 **接口说明** : 一次性返回词频、情感、主题、时间序列、热点等所有分析结果

 **请求方式** : `GET`

 **接口路径** : `/api/analysis/comprehensive`

 **认证要求** : ✅ 需要Token

#### 请求参数

| 参数名     | 类型    | 必填 | 默认值   | 说明                                               |
| ---------- | ------- | ---- | -------- | -------------------------------------------------- |
| type       | string  | 否   | articles | 数据类型：`articles`(文章) 或 `comments`(评论) |
| days       | integer | 否   | 7        | 时间范围(天)，取值范围：1-90                       |
| article_id | string  | 否   | -        | 文章ID，仅当type=comments时有效                    |

#### 请求示例

```http
GET /api/analysis/comprehensive?type=articles&days=7
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 响应示例

```json
{
  "code": 200,
  "message": "综合分析完成",
  "data": {
    "success": true,
    "data_type": "articles",
    "time_range_days": 7,
    "total_items": 1250,
    "analysis_timestamp": "2026-01-11T10:30:00",
  
    "word_analysis": {
      "word_frequency": [
        {"word": "人工智能", "count": 328},
        {"word": "技术", "count": 256}
      ],
      "keywords_tfidf": [
        {"word": "人工智能", "weight": 0.8523},
        {"word": "深度学习", "weight": 0.7234}
      ],
      "keywords_textrank": [
        {"word": "人工智能", "weight": 0.9123},
        {"word": "机器学习", "weight": 0.8456}
      ],
      "total_words": 15680,
      "unique_words": 3420,
      "vocabulary_diversity": 0.2180
    },
  
    "sentiment_analysis": {
      "detailed_results": [
        {
          "text_id": 0,
          "text_preview": "人工智能技术发展迅速...",
          "sentiment_score": 0.8523,
          "sentiment_label": "positive",
          "sentiment_intensity": "strong",
          "text_length": 156
        }
      ],
      "statistics": {
        "average_sentiment": 0.6234,
        "median_sentiment": 0.6500,
        "std_sentiment": 0.1823,
        "positive_count": 756,
        "negative_count": 234,
        "neutral_count": 260,
        "total_analyzed": 1250,
        "positive_ratio": 0.6048,
        "negative_ratio": 0.1872,
        "neutral_ratio": 0.2080
      },
      "sentiment_distribution": {
        "very_negative": 45,
        "negative": 189,
        "neutral": 260,
        "positive": 568,
        "very_positive": 188
      }
    },
  
    "topic_analysis": {
      "topics": [
        {
          "topic_id": 0,
          "topic_name": "主题 1",
          "keywords": [
            {"word": "人工智能", "weight": 0.0523},
            {"word": "技术", "weight": 0.0456}
          ],
          "coherence": 0.8234
        }
      ],
      "n_topics": 5,
      "perplexity": 234.5678,
      "doc_topic_distribution": {
        "topic_0": 345,
        "topic_1": 289,
        "topic_2": 256,
        "topic_3": 198,
        "topic_4": 162
      }
    },
  
    "temporal_analysis": {
      "daily_distribution": [
        {"date": "2026-01-05", "count": 178},
        {"date": "2026-01-06", "count": 192}
      ],
      "hourly_distribution": [
        {"hour": "2026-01-11 08:00", "count": 45},
        {"hour": "2026-01-11 09:00", "count": 67}
      ],
      "weekday_distribution": [
        {"weekday": "Monday", "count": 234},
        {"weekday": "Tuesday", "count": 198}
      ],
      "trend_analysis": {
        "trend_direction": "increasing",
        "peak_hours": [
          "2026-01-11 09:00",
          "2026-01-11 14:00"
        ],
        "total_days": 7,
        "avg_daily_count": 178.57
      }
    },
  
    "hotspot_analysis": {
      "trending_hashtags": [
        {"hashtag": "人工智能", "count": 234},
        {"hashtag": "科技创新", "count": 189}
      ],
      "trending_mentions": [
        {"mention": "科技日报", "count": 156},
        {"mention": "AI研究院", "count": 123}
      ],
      "hot_contents": [
        {
          "content_id": "507f1f77bcf86cd799439011",
          "text_preview": "人工智能技术取得重大突破...",
          "heat_score": 5678,
          "reposts": 1234,
          "comments": 567,
          "likes": 2345,
          "created_at": "2026-01-10T15:30:00"
        }
      ],
      "propagation_analysis": {
        "total_engagement": 125678,
        "total_reposts": 34567,
        "total_comments": 23456,
        "total_likes": 67655,
        "avg_reposts": 27.65,
        "avg_comments": 18.76,
        "avg_likes": 54.12
      },
      "total_hashtags": 234,
      "total_mentions": 189
    }
  }
}
```

#### 错误响应

```json
{
  "code": 400,
  "message": "类型必须是articles或comments",
  "data": null
}
```

```json
{
  "code": 400,
  "message": "时间范围必须在1-90天之间",
  "data": null
}
```

---

## 图表生成接口

### 2. 生成词云图表

 **接口说明** : 根据词频数据生成ECharts词云图配置

 **请求方式** : `POST`

 **接口路径** : `/api/analysis/charts/word-cloud`

 **认证要求** : ✅ 需要Token

#### 请求参数

```json
{
  "word_data": [
    {"word": "人工智能", "count": 328},
    {"word": "技术", "count": 256},
    {"word": "创新", "count": 198}
  ]
}
```

| 参数名            | 类型    | 必填 | 说明         |
| ----------------- | ------- | ---- | ------------ |
| word_data         | array   | 是   | 词频数据数组 |
| word_data[].word  | string  | 是   | 词语         |
| word_data[].count | integer | 是   | 出现次数     |

#### 响应示例

```json
{
  "code": 200,
  "message": "词云图表生成成功",
  "data": {
    "chart_options": "{\"title\":[{\"text\":\"词云分析\"}],\"series\":[{\"type\":\"wordCloud\",\"data\":[[\"人工智能\",328],[\"技术\",256]]}]}"
  }
}
```

---

### 3. 生成情感饼图

 **接口说明** : 根据情感统计数据生成饼图配置

 **请求方式** : `POST`

 **接口路径** : `/api/analysis/charts/sentiment-pie`

 **认证要求** : ✅ 需要Token

#### 请求参数

```json
{
  "sentiment_stats": {
    "positive_count": 756,
    "negative_count": 234,
    "neutral_count": 260
  }
}
```

| 参数名                         | 类型    | 必填 | 说明         |
| ------------------------------ | ------- | ---- | ------------ |
| sentiment_stats                | object  | 是   | 情感统计对象 |
| sentiment_stats.positive_count | integer | 是   | 积极情感数量 |
| sentiment_stats.negative_count | integer | 是   | 消极情感数量 |
| sentiment_stats.neutral_count  | integer | 是   | 中性情感数量 |

#### 响应示例

```json
{
  "code": 200,
  "message": "情感饼图生成成功",
  "data": {
    "chart_options": "{\"title\":[{\"text\":\"情感分布\"}],\"series\":[{\"type\":\"pie\",\"radius\":[\"40%\",\"75%\"],\"data\":[[\"积极\",756],[\"中性\",260],[\"消极\",234]]}]}"
  }
}
```

---

### 4. 生成时间趋势图

 **接口说明** : 根据时间序列数据生成折线图配置

 **请求方式** : `POST`

 **接口路径** : `/api/analysis/charts/temporal-line`

 **认证要求** : ✅ 需要Token

#### 请求参数

```json
{
  "daily_data": [
    {"date": "2026-01-05", "count": 178},
    {"date": "2026-01-06", "count": 192},
    {"date": "2026-01-07", "count": 205}
  ]
}
```

| 参数名             | 类型    | 必填 | 说明             |
| ------------------ | ------- | ---- | ---------------- |
| daily_data         | array   | 是   | 每日数据数组     |
| daily_data[].date  | string  | 是   | 日期(YYYY-MM-DD) |
| daily_data[].count | integer | 是   | 数量             |

#### 响应示例

```json
{
  "code": 200,
  "message": "时间趋势图生成成功",
  "data": {
    "chart_options": "{\"title\":[{\"text\":\"时间趋势分析\"}],\"xAxis\":[{\"type\":\"category\",\"data\":[\"2026-01-05\",\"2026-01-06\"]}],\"series\":[{\"name\":\"数量\",\"type\":\"line\",\"smooth\":true,\"data\":[178,192]}]}"
  }
}
```

---

## 错误码说明

| 错误码 | 说明           | 解决方案                   |
| ------ | -------------- | -------------------------- |
| 200    | 请求成功       | -                          |
| 400    | 请求参数错误   | 检查请求参数格式和取值范围 |
| 401    | 未授权         | 检查Token是否有效          |
| 403    | 禁止访问       | 检查用户权限               |
| 404    | 资源不存在     | 检查请求路径               |
| 500    | 服务器内部错误 | 联系技术支持               |

---

## 数据字典

### 情感分类标准

| 情感标签 | 分数范围  | 说明     |
| -------- | --------- | -------- |
| positive | 0.7 - 1.0 | 积极情感 |
| neutral  | 0.3 - 0.7 | 中性情感 |
| negative | 0.0 - 0.3 | 消极情感 |

### 情感强度分类

| 强度标签 | 条件                                     | 说明     |
| -------- | ---------------------------------------- | -------- |
| strong   | score ≥ 0.8 或 score ≤ 0.2             | 强烈情感 |
| moderate | 0.6 ≤ score < 0.8 或 0.2 < score ≤ 0.4 | 中等强度 |
| weak     | 0.4 < score < 0.6                        | 弱情感   |

### 趋势方向

| 趋势值     | 说明     |
| ---------- | -------- |
| increasing | 上升趋势 |
| decreasing | 下降趋势 |
| stable     | 稳定     |

---

## 使用示例

### Python示例

```python
import requests

# 配置
base_url = "http://your-domain.com/api"
token = "your_jwt_token"

# 请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. 综合分析
response = requests.get(
    f"{base_url}/analysis/comprehensive",
    params={"type": "articles", "days": 7},
    headers=headers
)
result = response.json()
print(result)

# 2. 生成词云图表
word_data = result["data"]["word_analysis"]["word_frequency"]
response = requests.post(
    f"{base_url}/analysis/charts/word-cloud",
    json={"word_data": word_data},
    headers=headers
)
chart_options = response.json()["data"]["chart_options"]
```

### JavaScript示例

```javascript
const baseUrl = 'http://your-domain.com/api';
const token = 'your_jwt_token';

// 综合分析
async function comprehensiveAnalysis() {
  const response = await fetch(
    `${baseUrl}/analysis/comprehensive?type=articles&days=7`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const result = await response.json();
  console.log(result);
  return result;
}

// 生成词云
async function generateWordCloud(wordData) {
  const response = await fetch(
    `${baseUrl}/analysis/charts/word-cloud`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ word_data: wordData })
    }
  );
  const result = await response.json();
  return result.data.chart_options;
}
```

---

## 注意事项

1. **性能优化**
   * 建议时间范围不超过30天以获得最佳性能
   * 大规模数据分析可能需要10-30秒响应时间
2. **数据要求**
   * 主题分析至少需要10条文本数据
   * 文本长度建议不少于5个字符
3. **并发限制**
   * 单用户并发请求上限：5个/秒
   * 建议使用缓存机制减少重复请求
4. **数据更新**
   * MongoDB数据实时同步
   * 分析结果不缓存，每次请求重新计算
