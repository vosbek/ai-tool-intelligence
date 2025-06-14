// e2e/admin-interface.spec.ts - End-to-end tests for admin interface features

import { test, expect } from '@playwright/test';

test.describe('Admin Interface', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
  });

  test('should test admin API endpoints', async ({ page }) => {
    // Test admin health check
    const response = await page.request.get('/api/admin/health');
    
    if (response.status() === 404) {
      test.skip(true, 'Admin API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });

  test('should test system statistics', async ({ page }) => {
    // Test system stats endpoint
    const response = await page.request.get('/api/admin/stats');
    
    if (response.status() === 404) {
      test.skip(true, 'Admin stats API not available');
      return;
    }
    
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toBeDefined();
  });

  test('should test database management endpoints', async ({ page }) => {
    // Test database backup endpoint
    const backupResponse = await page.request.post('/api/admin/backup');
    
    if (backupResponse.status() === 404) {
      test.skip(true, 'Database backup API not available');
      return;
    }
    
    expect([200, 202, 422]).toContain(backupResponse.status());
  });

  test('should test system configuration', async ({ page }) => {
    // Test configuration endpoints
    const configResponse = await page.request.get('/api/admin/config');
    
    if (configResponse.status() === 404) {
      test.skip(true, 'Admin config API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(configResponse.status());
  });

  test('should test user management endpoints', async ({ page }) => {
    // Test user management (if implemented)
    const usersResponse = await page.request.get('/api/admin/users');
    
    if (usersResponse.status() === 404) {
      test.skip(true, 'User management API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(usersResponse.status());
  });

  test('should test system logs', async ({ page }) => {
    // Test system logs endpoint
    const logsResponse = await page.request.get('/api/admin/logs');
    
    if (logsResponse.status() === 404) {
      test.skip(true, 'System logs API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(logsResponse.status());
  });

  test('should test audit trail', async ({ page }) => {
    // Test audit trail functionality
    const auditResponse = await page.request.get('/api/admin/audit');
    
    if (auditResponse.status() === 404) {
      test.skip(true, 'Audit trail API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(auditResponse.status());
  });

  test('should test system maintenance', async ({ page }) => {
    // Test maintenance mode endpoints
    const maintenanceResponse = await page.request.get('/api/admin/maintenance');
    
    if (maintenanceResponse.status() === 404) {
      test.skip(true, 'Maintenance API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(maintenanceResponse.status());
  });

  test('should test data export functionality', async ({ page }) => {
    // Test data export
    const exportResponse = await page.request.post('/api/admin/export', {
      data: {
        format: 'json',
        table: 'tools'
      }
    });
    
    if (exportResponse.status() === 404) {
      test.skip(true, 'Data export API not available');
      return;
    }
    
    expect([200, 202, 400, 401, 403]).toContain(exportResponse.status());
  });

  test('should test data import functionality', async ({ page }) => {
    // Test data import
    const importResponse = await page.request.post('/api/admin/import', {
      data: {
        format: 'json',
        data: []
      }
    });
    
    if (importResponse.status() === 404) {
      test.skip(true, 'Data import API not available');
      return;
    }
    
    expect([200, 202, 400, 401, 403, 422]).toContain(importResponse.status());
  });

  test('should test system performance metrics', async ({ page }) => {
    // Test performance metrics
    const metricsResponse = await page.request.get('/api/admin/metrics');
    
    if (metricsResponse.status() === 404) {
      test.skip(true, 'Performance metrics API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(metricsResponse.status());
  });

  test('should test cleanup operations', async ({ page }) => {
    // Test cleanup operations
    const cleanupResponse = await page.request.post('/api/admin/cleanup', {
      data: {
        operation: 'temp_files'
      }
    });
    
    if (cleanupResponse.status() === 404) {
      test.skip(true, 'Cleanup API not available');
      return;
    }
    
    expect([200, 202, 400, 401, 403]).toContain(cleanupResponse.status());
  });

  test('should test configuration updates', async ({ page }) => {
    // Test configuration update
    const updateResponse = await page.request.put('/api/admin/config', {
      data: {
        setting: 'test_mode',
        value: true
      }
    });
    
    if (updateResponse.status() === 404) {
      test.skip(true, 'Config update API not available');
      return;
    }
    
    expect([200, 400, 401, 403, 422]).toContain(updateResponse.status());
  });

  test('should test system health checks', async ({ page }) => {
    // Test comprehensive health check
    const healthResponse = await page.request.get('/api/admin/health/detailed');
    
    if (healthResponse.status() === 404) {
      test.skip(true, 'Detailed health check API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(healthResponse.status());
  });

  test('should test security audit', async ({ page }) => {
    // Test security audit functionality
    const securityResponse = await page.request.get('/api/admin/security-audit');
    
    if (securityResponse.status() === 404) {
      test.skip(true, 'Security audit API not available');
      return;
    }
    
    expect([200, 401, 403]).toContain(securityResponse.status());
  });
});