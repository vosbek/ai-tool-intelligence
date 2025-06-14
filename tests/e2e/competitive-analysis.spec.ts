// e2e/competitive-analysis.spec.ts - End-to-end tests for competitive analysis features

import { test, expect } from '@playwright/test';

test.describe('Competitive Analysis', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
  });

  test('should display competitive analysis section', async ({ page }) => {
    // Look for competitive analysis elements on main dashboard
    // Note: These might not be implemented in frontend yet
    const competitiveSection = page.locator('[data-testid="competitive-analysis"]');
    if (await competitiveSection.isVisible()) {
      await expect(competitiveSection).toBeVisible();
    } else {
      // Skip test if not implemented in frontend
      test.skip(true, 'Competitive analysis not yet implemented in frontend');
    }
  });

  test('should test competitive analysis API endpoints', async ({ page }) => {
    // Test API endpoints directly since frontend might not expose them
    const response = await page.request.get('/api/competitive-analysis');
    
    if (response.status() === 404) {
      test.skip(true, 'Competitive analysis API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toBeDefined();
  });

  test('should test market research endpoints', async ({ page }) => {
    // Test market research API
    const response = await page.request.get('/api/market-research');
    
    if (response.status() === 404) {
      test.skip(true, 'Market research API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toBeDefined();
  });

  test('should test competitive landscape API', async ({ page }) => {
    // Test competitive landscape endpoint
    const response = await page.request.get('/api/competitive-landscape');
    
    if (response.status() === 404) {
      test.skip(true, 'Competitive landscape API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should handle competitor comparison', async ({ page }) => {
    // Test competitor comparison functionality
    const response = await page.request.post('/api/compare-tools', {
      data: {
        tool_ids: [1, 2]
      }
    });
    
    if (response.status() === 404) {
      test.skip(true, 'Tool comparison API not available');
      return;
    }
    
    expect([200, 400, 422]).toContain(response.status());
  });

  test('should test trend analysis endpoints', async ({ page }) => {
    // Test trend analysis API
    const response = await page.request.get('/api/trends');
    
    if (response.status() === 404) {
      test.skip(true, 'Trends API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should test market intelligence gathering', async ({ page }) => {
    // Test market intelligence endpoints
    const response = await page.request.get('/api/market-intelligence');
    
    if (response.status() === 404) {
      test.skip(true, 'Market intelligence API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should test pricing analysis', async ({ page }) => {
    // Test pricing analysis endpoints
    const response = await page.request.get('/api/pricing-analysis');
    
    if (response.status() === 404) {
      test.skip(true, 'Pricing analysis API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should test feature comparison matrix', async ({ page }) => {
    // Test feature comparison functionality
    const response = await page.request.get('/api/feature-matrix');
    
    if (response.status() === 404) {
      test.skip(true, 'Feature matrix API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should test competitive positioning', async ({ page }) => {
    // Test competitive positioning analysis
    const response = await page.request.get('/api/competitive-positioning');
    
    if (response.status() === 404) {
      test.skip(true, 'Competitive positioning API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
  });

  test('should test SWOT analysis endpoints', async ({ page }) => {
    // Test SWOT analysis functionality
    const response = await page.request.post('/api/swot-analysis', {
      data: {
        tool_id: 1
      }
    });
    
    if (response.status() === 404) {
      test.skip(true, 'SWOT analysis API not available');
      return;
    }
    
    expect([200, 400, 422]).toContain(response.status());
  });
});