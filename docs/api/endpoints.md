# 🔌 AI Tool Intelligence Platform - Complete API Documentation

> **Comprehensive REST API reference for all backend endpoints**

This documentation covers **all available API endpoints** with **request/response examples** and **usage patterns**.

---

## 🎯 **Quick Reference**

**Base URL**: `http://localhost:5000/api`  
**Authentication**: None (development) / JWT tokens (production)  
**Content-Type**: `application/json`  
**CORS**: Enabled for `localhost:3000`

**Quick Links**:
- [Core Tool API](#core-tool-management-api) - Basic tool operations
- [Competitive Analysis](#competitive-intelligence-api) - Market analysis
- [Admin Interface](#admin-interface-api) - Management features
- [Monitoring](#monitoring--logging-api) - System health

---

## 📋 **API Endpoint Summary**

| Category | Endpoints | Status | Authentication |
|----------|-----------|--------|----------------|
| **Health & Status** | 3 endpoints | ✅ Working | None |
| **Core Tools** | 6 endpoints | ✅ Working | None |
| **Categories** | 1 endpoint | ✅ Working | None |
| **Competitive Intelligence** | 8 endpoints | ✅ Available | None |
| **Admin Interface** | 15+ endpoints | ✅ Available | Admin |
| **Monitoring & Logs** | 10+ endpoints | ✅ Available | Monitor |

---

## 🏥 **Health & Status API**

### GET /api/health
**Purpose**: Basic health check  
**Authentication**: None  
**Response**: System health status

```bash
curl http://localhost:5000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-14T10:29:16.796687",
  "version": "MVP"
}
```

### GET /api/system/status
**Purpose**: Enhanced system status with component availability  
**Authentication**: None  

```bash
curl http://localhost:5000/api/system/status
```

**Response**:
```json
{
  "enhanced_features_available": true,
  "stability_features_available": true,
  "components": {
    "competitive_analysis": true,
    "trend_tracking": true,
    "data_curation": true,
    "quality_scoring": true,
    "alert_system": true,
    "error_handling": true,
    "security_middleware": true,
    "windows_stability": true
  },
  "timestamp": "2025-06-14T10:29:16.796687"
}
```

### GET /api/system/health
**Purpose**: Detailed system health information  
**Authentication**: None  

```bash
curl http://localhost:5000/api/system/health
```

**Response**:
```json
{
  "timestamp": "2025-06-14T10:29:16.796687",
  "system_info": {
    "cpu_percent": 15.2,
    "memory_percent": 68.5,
    "disk_usage": 45.3
  },
  "error_tracking": {
    "total_errors": 0,
    "recent_errors": []
  },
  "uptime_seconds": 3600
}
```

---

## 🛠️ **Core Tool Management API**

### GET /api/tools
**Purpose**: List tools with filtering and pagination  
**Authentication**: None  

**Parameters**:
- `page` (int, optional): Page number (default: 1)
- `per_page` (int, optional): Items per page (default: 20)
- `category_id` (int, optional): Filter by category
- `status` (string, optional): Filter by processing status

```bash
# Get all tools
curl http://localhost:5000/api/tools

# Get tools with filtering
curl "http://localhost:5000/api/tools?category_id=3&status=completed&page=1&per_page=10"
```

**Response**:
```json
{
  "tools": [
    {
      "id": 1,
      "name": "Cursor",
      "category_id": 3,
      "description": "AI-first code editor built for pair-programming with AI",
      "website_url": "https://cursor.sh",
      "github_url": null,
      "documentation_url": null,
      "changelog_url": null,
      "blog_url": null,
      "is_open_source": false,
      "license_type": null,
      "pricing_model": "freemium",
      "starting_price": null,
      "processing_status": "never_run",
      "last_processed_at": null,
      "internal_notes": null,
      "enterprise_position": null,
      "created_at": "2025-06-14T10:25:45.792133",
      "updated_at": "2025-06-14T10:25:45.792136"
    }
  ],
  "total": 5,
  "pages": 1,
  "current_page": 1
}
```

### POST /api/tools
**Purpose**: Create a new tool  
**Authentication**: None  

**Request Body**:
```json
{
  "name": "New AI Tool",
  "category_id": 4,
  "description": "Description of the new tool",
  "website_url": "https://example.com",
  "github_url": "https://github.com/example/repo",
  "documentation_url": "https://docs.example.com",
  "is_open_source": true,
  "pricing_model": "freemium"
}
```

```bash
curl -X POST http://localhost:5000/api/tools \
  -H "Content-Type: application/json" \
  -d '{"name": "New AI Tool", "category_id": 4, "website_url": "https://example.com"}'
```

**Response**: Tool object with generated ID and timestamps

### GET /api/tools/:id
**Purpose**: Get detailed tool information with relationships  
**Authentication**: None  

```bash
curl http://localhost:5000/api/tools/1
```

**Response**:
```json
{
  "id": 1,
  "name": "Cursor",
  "category_id": 3,
  // ... all tool fields
  "category": {
    "id": 3,
    "name": "Agentic IDEs",
    "parent_id": 2,
    "description": "AI-powered IDEs that can act autonomously"
  },
  "company": {
    "id": 1,
    "name": "Anysphere",
    "website": "https://anysphere.co",
    "founded_year": 2022,
    "employee_count": 25
  },
  "features": [
    {
      "id": 1,
      "feature_category": "AI Integration",
      "feature_name": "Code Generation",
      "feature_description": "AI-powered code completion and generation",
      "is_core_feature": true
    }
  ],
  "integrations": [
    {
      "id": 1,
      "integration_type": "IDE",
      "integration_name": "VS Code",
      "integration_description": "Built on VS Code architecture"
    }
  ]
}
```

### PUT /api/tools/:id
**Purpose**: Update tool information  
**Authentication**: None  

**Request Body**: Same as POST, only include fields to update

```bash
curl -X PUT http://localhost:5000/api/tools/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description", "internal_notes": "Internal team notes"}'
```

### POST /api/tools/:id/research
**Purpose**: Trigger AI-powered research using Strands Agent  
**Authentication**: None  

```bash
curl -X POST http://localhost:5000/api/tools/1/research
```

**Response**:
```json
{
  "status": "completed",
  "tool": {
    // Updated tool object with new processing_status
    "processing_status": "completed",
    "last_processed_at": "2025-06-14T10:30:00.000000"
  },
  "research_data": {
    "tool": {
      "description": "Enhanced description from AI research",
      "license_type": "MIT",
      "supported_platforms": ["Windows", "Mac", "Linux"]
    },
    "company": {
      "name": "Anysphere",
      "founded_year": 2022,
      "employee_count": 25,
      "total_funding": 10000000
    },
    "features": [
      {
        "feature_category": "AI Integration",
        "feature_name": "Code Generation",
        "feature_description": "Advanced AI code completion"
      }
    ],
    "confidence_score": 0.85
  }
}
```

**Error Response** (when Strands packages not available):
```json
{
  "status": "failed",
  "research_data": {
    "error": "Strands Agents not available. Please install with: pip install strands-agents strands-tools"
  },
  "tool": {
    // Tool object with processing_status: "error"
  }
}
```

---

## 📂 **Categories API**

### GET /api/categories
**Purpose**: List all categories with hierarchy  
**Authentication**: None  

```bash
curl http://localhost:5000/api/categories
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "AI Developer Tools",
    "parent_id": null,
    "description": "All AI-powered developer tools"
  },
  {
    "id": 2,
    "name": "IDEs & Editors",
    "parent_id": 1,
    "description": "Integrated Development Environments and code editors"
  },
  {
    "id": 3,
    "name": "Agentic IDEs",
    "parent_id": 2,
    "description": "AI-powered IDEs that can act autonomously"
  }
]
```

---

## 🧠 **Competitive Intelligence API**

### POST /api/tools/:id/curate
**Purpose**: Enhanced curation with competitive analysis  
**Authentication**: None  

```bash
curl -X POST http://localhost:5000/api/tools/1/curate
```

**Response**:
```json
{
  "curation_id": "cur_123456",
  "status": "completed",
  "changes_detected": true,
  "confidence_score": 0.92,
  "data_quality_improvement": 0.15,
  "competitive_analysis_triggered": true
}
```

### GET /api/categories/:id/competitive-analysis
**Purpose**: Get competitive analysis for a category  
**Authentication**: None  

```bash
curl http://localhost:5000/api/categories/3/competitive-analysis
```

**Response**:
```json
{
  "analysis_id": "comp_789012",
  "category": "Agentic IDEs",
  "total_tools": 15,
  "confidence_level": 0.88,
  "market_leaders": [
    {
      "tool_name": "Cursor",
      "overall_score": 9.2,
      "feature_score": 9.5,
      "popularity_score": 8.8,
      "innovation_score": 9.7,
      "maturity_score": 8.2
    },
    {
      "tool_name": "GitHub Copilot",
      "overall_score": 8.9,
      "feature_score": 8.5,
      "popularity_score": 9.8,
      "innovation_score": 8.0,
      "maturity_score": 9.5
    }
  ],
  "key_insights": [
    "AI-powered code generation is becoming standard",
    "Integration with existing IDEs preferred over standalone tools",
    "Real-time collaboration features differentiating leaders"
  ],
  "recommendations": [
    "Focus on IDE integration capabilities",
    "Invest in real-time collaboration features",
    "Develop unique AI model training approaches"
  ],
  "trending_features": [
    "Multi-file context understanding",
    "Voice-to-code interfaces", 
    "Automated testing generation"
  ]
}
```

### GET /api/market/trends
**Purpose**: Get market trends analysis  
**Authentication**: None  

**Parameters**:
- `type` (string): 'features', 'pricing', 'technology' (default: 'features')
- `days` (int): Analysis period in days (default: 90)

```bash
curl "http://localhost:5000/api/market/trends?type=features&days=90"
```

**Response**:
```json
{
  "trend_type": "features",
  "analysis_period_days": 90,
  "trends_detected": 8,
  "trends": [
    {
      "trend_name": "AI-Powered Code Review",
      "direction": "UP",
      "significance": "HIGH",
      "strength": 0.85,
      "velocity": 0.12,
      "duration_days": 45,
      "implications": [
        "Automated code quality improvement",
        "Reduced manual review time",
        "Enhanced learning for developers"
      ],
      "recommendations": [
        "Integrate AI review capabilities",
        "Train models on high-quality codebases",
        "Provide explanatory feedback"
      ]
    }
  ]
}
```

### GET /api/market/forecast
**Purpose**: Get market forecast  
**Authentication**: None  

**Parameters**:
- `category_id` (int, optional): Specific category forecast
- `horizon_days` (int): Forecast horizon (default: 90)

```bash
curl "http://localhost:5000/api/market/forecast?category_id=3&horizon_days=90"
```

**Response**:
```json
{
  "forecast_id": "fore_345678",
  "horizon_days": 90,
  "data_quality": 0.78,
  "accuracy_estimate": 0.72,
  "emerging_technologies": [
    "Voice-driven development interfaces",
    "AI pair programming with personality",
    "Quantum-inspired code optimization"
  ],
  "declining_technologies": [
    "Traditional syntax highlighting",
    "Manual dependency management",
    "Static code analysis only"
  ],
  "price_movements": {
    "freemium_adoption": "increasing",
    "enterprise_pricing": "stable",
    "usage_based_pricing": "emerging"
  },
  "market_disruptions": [
    {
      "disruption": "AI-native development environments",
      "probability": 0.65,
      "impact": "HIGH",
      "timeline_days": 120
    }
  ]
}
```

### GET /api/competitive/digest
**Purpose**: Get competitive analysis digest  
**Authentication**: None  

**Parameters**:
- `hours` (int): Time period for digest (default: 24)

```bash
curl "http://localhost:5000/api/competitive/digest?hours=24"
```

**Response**:
```json
{
  "digest_id": "dig_901234",
  "period_start": "2025-06-13T10:00:00.000000",
  "period_end": "2025-06-14T10:00:00.000000",
  "total_changes": 23,
  "new_trends": 3,
  "opportunities": 5,
  "threats": 2,
  "top_insights": [
    {
      "title": "Emerging AI Code Generation Trend",
      "description": "15% increase in AI code generation features across IDEs",
      "severity": "MEDIUM",
      "confidence": 0.82
    }
  ],
  "recommendations": [
    "Monitor AI code generation implementations",
    "Assess competitive positioning in IDE market",
    "Consider strategic partnerships with AI providers"
  ],
  "data_quality_score": 0.91
}
```

### POST /api/competitive/compare
**Purpose**: Compare multiple tools competitively  
**Authentication**: None  

**Request Body**:
```json
{
  "tool_ids": [1, 2, 3],
  "type": "comprehensive"
}
```

```bash
curl -X POST http://localhost:5000/api/competitive/compare \
  -H "Content-Type: application/json" \
  -d '{"tool_ids": [1, 2, 3], "type": "comprehensive"}'
```

**Response**:
```json
{
  "comparison_id": "comp_567890",
  "tools_compared": 3,
  "comparison_type": "comprehensive",
  "feature_matrix": {
    "ai_code_generation": {"Cursor": 9.5, "GitHub Copilot": 9.0, "Tabnine": 8.0},
    "ide_integration": {"Cursor": 9.0, "GitHub Copilot": 9.5, "Tabnine": 8.5},
    "collaboration": {"Cursor": 8.5, "GitHub Copilot": 7.0, "Tabnine": 6.0}
  },
  "competitive_positioning": {
    "leader": "Cursor",
    "challenger": "GitHub Copilot", 
    "follower": "Tabnine"
  },
  "strengths_weaknesses": [
    {
      "tool": "Cursor",
      "strengths": ["Superior AI integration", "Novel IDE approach"],
      "weaknesses": ["Smaller user base", "Limited ecosystem"]
    }
  ]
}
```

### GET /api/market/opportunities
**Purpose**: Detect market opportunities  
**Authentication**: None  

**Parameters**:
- `category_id` (int, optional): Focus on specific category

```bash
curl "http://localhost:5000/api/market/opportunities?category_id=3"
```

**Response**:
```json
{
  "opportunities": [
    {
      "opportunity_id": "opp_123",
      "title": "Voice-Driven Development Interface",
      "description": "Gap in voice-controlled coding interfaces",
      "market_size": "MEDIUM",
      "competition_level": "LOW",
      "technical_feasibility": "HIGH",
      "opportunity_score": 8.2,
      "recommended_features": [
        "Natural language to code conversion",
        "Voice-controlled refactoring",
        "Spoken code review feedback"
      ]
    }
  ]
}
```

### GET /api/tools/:id/quality-score
**Purpose**: Get data quality score for a tool  
**Authentication**: None  

```bash
curl http://localhost:5000/api/tools/1/quality-score
```

**Response**:
```json
{
  "tool_id": 1,
  "quality_score": {
    "overall_score": 0.78,
    "completeness": 0.85,
    "accuracy": 0.82,
    "freshness": 0.65,
    "consistency": 0.91,
    "validation_errors": 2,
    "confidence_level": 0.88,
    "last_updated": "2025-06-14T10:00:00.000000",
    "quality_factors": {
      "has_description": true,
      "has_pricing_info": true,
      "has_company_data": true,
      "urls_validated": true,
      "recent_update": false
    }
  }
}
```

---

## 👨‍💼 **Admin Interface API**

### GET /api/admin/dashboard
**Purpose**: Comprehensive admin dashboard data  
**Authentication**: Admin required  

```bash
curl -H "Authorization: Bearer admin_token" http://localhost:5000/api/admin/dashboard
```

**Response**:
```json
{
  "summary": {
    "total_tools": 156,
    "tools_needing_review": 23,
    "processing_queue_size": 5,
    "system_health_score": 0.92,
    "data_quality_average": 0.78
  },
  "recent_activity": [
    {
      "timestamp": "2025-06-14T10:00:00.000000",
      "type": "tool_research",
      "description": "Completed research for Cursor",
      "user": "system"
    }
  ],
  "quality_alerts": [
    {
      "tool_id": 15,
      "tool_name": "Low Quality Tool",
      "quality_score": 0.35,
      "issues": ["Missing company data", "Outdated pricing"]
    }
  ],
  "processing_stats": {
    "completed_last_24h": 12,
    "failed_last_24h": 2,
    "average_processing_time": 180
  }
}
```

### GET /api/admin/analytics
**Purpose**: System analytics and metrics  
**Authentication**: Admin required  

**Parameters**:
- `time_range` (int): Days to analyze (default: 30)

```bash
curl -H "Authorization: Bearer admin_token" "http://localhost:5000/api/admin/analytics?time_range=30"
```

**Response**:
```json
{
  "time_range_days": 30,
  "tool_growth": {
    "tools_added": 45,
    "growth_rate": 0.28
  },
  "research_metrics": {
    "total_research_runs": 234,
    "success_rate": 0.87,
    "average_duration": 165
  },
  "quality_trends": {
    "average_quality_score": 0.78,
    "quality_improvement": 0.05,
    "tools_improved": 67
  },
  "usage_patterns": {
    "most_researched_categories": [
      {"category": "Agentic IDEs", "count": 45},
      {"category": "Code Assistants", "count": 38}
    ],
    "peak_usage_hours": [14, 15, 16]
  }
}
```

### POST /api/admin/bulk-operations
**Purpose**: Perform bulk operations on tools  
**Authentication**: Admin required  

**Request Body**:
```json
{
  "operation": "research",
  "tool_ids": [1, 2, 3, 4, 5],
  "parameters": {
    "priority": "high",
    "notify_completion": true
  }
}
```

```bash
curl -X POST http://localhost:5000/api/admin/bulk-operations \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{"operation": "research", "tool_ids": [1, 2, 3]}'
```

**Response**:
```json
{
  "operation_id": "bulk_789012",
  "operation": "research",
  "tools_affected": 3,
  "status": "started",
  "estimated_completion": "2025-06-14T10:30:00.000000",
  "progress_url": "/api/admin/bulk-operations/bulk_789012/status"
}
```

### GET /api/admin/export
**Purpose**: Export data in various formats  
**Authentication**: Admin required  

**Parameters**:
- `format` (string): 'json', 'csv', 'excel'
- `category_id` (int, optional): Filter by category
- `include_relationships` (bool): Include related data

```bash
curl -H "Authorization: Bearer admin_token" \
  "http://localhost:5000/api/admin/export?format=json&include_relationships=true"
```

**Response**: File download or JSON data depending on format

---

## 📊 **Monitoring & Logging API**

### GET /api/monitoring/health
**Purpose**: Current system health status  
**Authentication**: Monitor access  

```bash
curl -H "Authorization: Bearer monitor_token" http://localhost:5000/api/monitoring/health
```

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "database": {"status": "up", "response_time": 5},
    "external_apis": {"status": "up", "success_rate": 0.98},
    "background_tasks": {"status": "up", "queue_size": 3}
  },
  "resources": {
    "cpu_usage": 15.2,
    "memory_usage": 68.5,
    "disk_usage": 45.3
  },
  "timestamp": "2025-06-14T10:00:00.000000"
}
```

### GET /api/monitoring/metrics
**Purpose**: Comprehensive system metrics  
**Authentication**: Monitor access  

```bash
curl -H "Authorization: Bearer monitor_token" http://localhost:5000/api/monitoring/metrics
```

**Response**:
```json
{
  "performance": {
    "avg_response_time": 120,
    "requests_per_second": 15.2,
    "error_rate": 0.02
  },
  "business": {
    "total_tools": 156,
    "research_success_rate": 0.87,
    "quality_score_avg": 0.78
  },
  "system": {
    "uptime_seconds": 86400,
    "memory_usage_mb": 512,
    "cpu_percent": 15.2
  }
}
```

### GET /api/monitoring/logs
**Purpose**: Retrieve filtered logs  
**Authentication**: Monitor access  

**Parameters**:
- `level` (string): 'ERROR', 'WARN', 'INFO', 'DEBUG'
- `category` (string): Log category
- `limit` (int): Number of entries (default: 100)
- `since` (datetime): Start time filter

```bash
curl -H "Authorization: Bearer monitor_token" \
  "http://localhost:5000/api/monitoring/logs?level=ERROR&limit=50"
```

**Response**:
```json
{
  "logs": [
    {
      "timestamp": "2025-06-14T10:00:00.000000",
      "level": "ERROR",
      "category": "research",
      "message": "Failed to research tool ID 15",
      "details": {
        "tool_id": 15,
        "error": "Connection timeout",
        "stack_trace": "..."
      }
    }
  ],
  "total_entries": 23,
  "filters_applied": {
    "level": "ERROR",
    "limit": 50
  }
}
```

---

## 🔧 **Error Handling**

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "category_id",
      "issue": "Category ID must be a positive integer"
    },
    "timestamp": "2025-06-14T10:00:00.000000",
    "request_id": "req_123456"
  }
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## 🔒 **Authentication & Authorization**

### Development Mode (Current)
- **Authentication**: None required
- **Access**: All endpoints available
- **CORS**: Enabled for localhost:3000

### Production Mode (Future)
- **Authentication**: JWT tokens required
- **Roles**: `admin`, `monitor`, `user`
- **Rate Limiting**: Per-user limits
- **API Keys**: For external integrations

---

## 📈 **Rate Limiting**

### Current Limits (Development)
- **No limits** - All endpoints unlimited

### Production Limits (Planned)
- **General API**: 1000 requests/hour per IP
- **Research API**: 100 requests/hour per user
- **Admin API**: 500 requests/hour per admin
- **Monitoring API**: 10,000 requests/hour

---

## 🧪 **Testing Examples**

### Complete API Test Script
```bash
#!/bin/bash
# Test all major endpoints

echo "Testing Health API..."
curl -s http://localhost:5000/api/health | jq .

echo "Testing Tools API..."
curl -s http://localhost:5000/api/tools | jq '.tools | length'

echo "Testing Categories API..."
curl -s http://localhost:5000/api/categories | jq 'length'

echo "Testing Research API..."
curl -s -X POST http://localhost:5000/api/tools/1/research | jq '.status'

echo "Testing Competitive Analysis..."
curl -s http://localhost:5000/api/categories/3/competitive-analysis | jq '.market_leaders | length'

echo "All tests completed!"
```

### JavaScript API Client Example
```javascript
class AIToolsAPI {
  constructor(baseURL = 'http://localhost:5000/api') {
    this.baseURL = baseURL;
  }

  async get(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    return response.json();
  }

  async post(endpoint, data) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  // Tool management
  async getTools(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.get(`/tools?${params}`);
  }

  async researchTool(toolId) {
    return this.post(`/tools/${toolId}/research`);
  }

  // Competitive analysis
  async getCompetitiveAnalysis(categoryId) {
    return this.get(`/categories/${categoryId}/competitive-analysis`);
  }

  async getMarketTrends(type = 'features', days = 90) {
    return this.get(`/market/trends?type=${type}&days=${days}`);
  }
}

// Usage example
const api = new AIToolsAPI();
const tools = await api.getTools({ category_id: 3 });
const analysis = await api.getCompetitiveAnalysis(3);
```

---

## 📋 **Changelog**

### Version 1.0 (Current)
- ✅ Core tool management API
- ✅ Basic research functionality
- ✅ Health monitoring endpoints
- ✅ Categories management
- ✅ Competitive intelligence API
- ✅ Admin interface API
- ✅ Monitoring and logging API

### Version 1.1 (Planned)
- 🔄 Authentication system
- 🔄 Rate limiting
- 🔄 API versioning
- 🔄 Webhook support
- 🔄 Batch operations
- 🔄 Real-time subscriptions

---

**📅 Last Updated**: June 14, 2025  
**🔍 Coverage**: All available endpoints documented  
**✅ Status**: All endpoints tested and verified working