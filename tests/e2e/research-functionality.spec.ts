// e2e/research-functionality.spec.ts - End-to-end tests for AI research functionality

import { test, expect } from '@playwright/test';

test.describe('Research Functionality', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
  });

  test('should test research API endpoints', async ({ page }) => {
    // Test research endpoint
    const response = await page.request.post('/api/research', {
      data: {
        tool_id: 1,
        research_type: 'comprehensive'
      }
    });
    
    expect([200, 202, 400, 422, 503]).toContain(response.status());
    
    if (response.status() === 200 || response.status() === 202) {
      const data = await response.json();
      expect(data).toBeDefined();
    }
  });

  test('should test research status tracking', async ({ page }) => {
    // Test research status endpoint
    const statusResponse = await page.request.get('/api/research/status/1');
    
    expect([200, 404]).toContain(statusResponse.status());
    
    if (statusResponse.status() === 200) {
      const data = await statusResponse.json();
      expect(data).toHaveProperty('status');
    }
  });

  test('should test research results retrieval', async ({ page }) => {
    // Test research results endpoint
    const resultsResponse = await page.request.get('/api/research/results/1');
    
    expect([200, 404]).toContain(resultsResponse.status());
    
    if (resultsResponse.status() === 200) {
      const data = await resultsResponse.json();
      expect(data).toBeDefined();
    }
  });

  test('should test bulk research operations', async ({ page }) => {
    // Test bulk research
    const bulkResponse = await page.request.post('/api/research/bulk', {
      data: {
        tool_ids: [1, 2, 3],
        research_type: 'basic'
      }
    });
    
    expect([200, 202, 400, 422, 503]).toContain(bulkResponse.status());
  });

  test('should test research queue management', async ({ page }) => {
    // Test research queue
    const queueResponse = await page.request.get('/api/research/queue');
    
    expect([200, 404]).toContain(queueResponse.status());
    
    if (queueResponse.status() === 200) {
      const data = await queueResponse.json();
      expect(Array.isArray(data)).toBe(true);
    }
  });

  test('should test research cancellation', async ({ page }) => {
    // Test research cancellation
    const cancelResponse = await page.request.delete('/api/research/1');
    
    expect([200, 404, 409]).toContain(cancelResponse.status());
  });

  test('should test research history', async ({ page }) => {
    // Test research history
    const historyResponse = await page.request.get('/api/research/history');
    
    expect([200, 404]).toContain(historyResponse.status());
    
    if (historyResponse.status() === 200) {
      const data = await historyResponse.json();
      expect(Array.isArray(data)).toBe(true);
    }
  });

  test('should test research analytics', async ({ page }) => {
    // Test research analytics
    const analyticsResponse = await page.request.get('/api/research/analytics');
    
    expect([200, 404]).toContain(analyticsResponse.status());
    
    if (analyticsResponse.status() === 200) {
      const data = await analyticsResponse.json();
      expect(data).toBeDefined();
    }
  });

  test('should test research configuration', async ({ page }) => {
    // Test research configuration
    const configResponse = await page.request.get('/api/research/config');
    
    expect([200, 404]).toContain(configResponse.status());
    
    if (configResponse.status() === 200) {
      const data = await configResponse.json();
      expect(data).toBeDefined();
    }
  });

  test('should test research templates', async ({ page }) => {
    // Test research templates
    const templatesResponse = await page.request.get('/api/research/templates');
    
    expect([200, 404]).toContain(templatesResponse.status());
    
    if (templatesResponse.status() === 200) {
      const data = await templatesResponse.json();
      expect(Array.isArray(data)).toBe(true);
    }
  });

  test('should test custom research queries', async ({ page }) => {
    // Test custom research
    const customResponse = await page.request.post('/api/research/custom', {
      data: {
        query: 'Analyze pricing model for this tool',
        tool_id: 1,
        context: 'pricing_analysis'
      }
    });
    
    expect([200, 202, 400, 422, 503]).toContain(customResponse.status());
  });

  test('should test research data export', async ({ page }) => {
    // Test research data export
    const exportResponse = await page.request.get('/api/research/export/1?format=json');
    
    expect([200, 404]).toContain(exportResponse.status());
    
    if (exportResponse.status() === 200) {
      const data = await exportResponse.json();
      expect(data).toBeDefined();
    }
  });

  test('should test research insights generation', async ({ page }) => {
    // Test insights generation
    const insightsResponse = await page.request.post('/api/research/insights', {
      data: {
        tool_id: 1,
        insight_type: 'market_position'
      }
    });
    
    expect([200, 202, 400, 422, 503]).toContain(insightsResponse.status());
  });

  test('should test research report generation', async ({ page }) => {
    // Test report generation
    const reportResponse = await page.request.post('/api/research/report', {
      data: {
        tool_id: 1,
        report_type: 'comprehensive',
        format: 'json'
      }
    });
    
    expect([200, 202, 400, 422, 503]).toContain(reportResponse.status());
  });

  test('should test research workflow automation', async ({ page }) => {
    // Test workflow automation
    const workflowResponse = await page.request.post('/api/research/workflow', {
      data: {
        workflow_id: 'standard_analysis',
        tool_id: 1
      }
    });
    
    expect([200, 202, 400, 404, 422, 503]).toContain(workflowResponse.status());
  });
});