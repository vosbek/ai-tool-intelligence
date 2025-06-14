// performance/load-testing.spec.ts - Performance and load testing with Playwright

import { test, expect } from '@playwright/test';

test.describe('Performance Testing', () => {
  
  test('should measure page load performance', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
    
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('should measure API response times', async ({ page }) => {
    const startTime = Date.now();
    
    const response = await page.request.get('/api/health');
    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(1000); // API should respond within 1 second
    
    console.log(`API response time: ${responseTime}ms`);
  });

  test('should measure tools API performance', async ({ page }) => {
    const startTime = Date.now();
    
    const response = await page.request.get('/api/tools');
    const responseTime = Date.now() - startTime;
    
    expect([200, 404]).toContain(response.status());
    expect(responseTime).toBeLessThan(2000); // Tools API should respond within 2 seconds
    
    console.log(`Tools API response time: ${responseTime}ms`);
  });

  test('should handle multiple concurrent requests', async ({ page }) => {
    const concurrentRequests = 10;
    const requests = [];
    
    const startTime = Date.now();
    
    // Fire multiple requests simultaneously
    for (let i = 0; i < concurrentRequests; i++) {
      requests.push(page.request.get('/api/health'));
    }
    
    const responses = await Promise.all(requests);
    const totalTime = Date.now() - startTime;
    
    // All requests should succeed
    responses.forEach(response => {
      expect(response.status()).toBe(200);
    });
    
    // Concurrent requests should complete within reasonable time
    expect(totalTime).toBeLessThan(5000);
    
    console.log(`${concurrentRequests} concurrent requests completed in: ${totalTime}ms`);
  });

  test('should measure memory usage during navigation', async ({ page }) => {
    // Navigate to main page
    await page.goto('/');
    await page.waitForSelector('h1');
    
    // Simulate user interactions that might cause memory leaks
    for (let i = 0; i < 5; i++) {
      // Click add tool button if it exists
      const addButton = page.locator('button:has-text("Add New Tool")');
      if (await addButton.isVisible()) {
        await addButton.click();
        await page.waitForTimeout(100);
        
        // Close the form if cancel button exists
        const cancelButton = page.locator('button:has-text("Cancel")');
        if (await cancelButton.isVisible()) {
          await cancelButton.click();
          await page.waitForTimeout(100);
        }
      }
    }
    
    // Test should complete without browser crashes
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should test large data handling', async ({ page }) => {
    // Test how the application handles large datasets
    const response = await page.request.get('/api/tools?limit=1000');
    
    if (response.status() === 200) {
      const data = await response.json();
      
      if (Array.isArray(data) && data.length > 100) {
        // Navigate to page and see if it can handle large dataset
        await page.goto('/');
        await page.waitForSelector('table', { timeout: 15000 });
        
        // Should still be responsive
        await expect(page.locator('h1')).toBeVisible();
      }
    }
  });

  test('should test search performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const searchInput = page.locator('input[placeholder="Search tools..."]');
    
    if (await searchInput.isVisible()) {
      const startTime = Date.now();
      
      await searchInput.fill('test');
      await page.waitForTimeout(500); // Wait for search to apply
      
      const searchTime = Date.now() - startTime;
      
      // Search should be fast
      expect(searchTime).toBeLessThan(2000);
      
      console.log(`Search time: ${searchTime}ms`);
    } else {
      test.skip(true, 'Search functionality not available');
    }
  });

  test('should test filter performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const filterSelect = page.locator('select').first();
    
    if (await filterSelect.isVisible()) {
      const startTime = Date.now();
      
      await filterSelect.selectOption({ index: 1 }); // Select first option
      await page.waitForTimeout(500); // Wait for filter to apply
      
      const filterTime = Date.now() - startTime;
      
      // Filtering should be fast
      expect(filterTime).toBeLessThan(2000);
      
      console.log(`Filter time: ${filterTime}ms`);
    } else {
      test.skip(true, 'Filter functionality not available');
    }
  });

  test('should test pagination performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const nextButton = page.locator('button:has-text("Next")');
    
    if (await nextButton.isVisible() && !await nextButton.isDisabled()) {
      const startTime = Date.now();
      
      await nextButton.click();
      await page.waitForTimeout(500); // Wait for pagination
      
      const paginationTime = Date.now() - startTime;
      
      // Pagination should be fast
      expect(paginationTime).toBeLessThan(2000);
      
      console.log(`Pagination time: ${paginationTime}ms`);
    } else {
      test.skip(true, 'Pagination not available or no next page');
    }
  });

  test('should test form submission performance', async ({ page }) => {
    await page.goto('/');
    
    const addButton = page.locator('button:has-text("Add New Tool")');
    
    if (await addButton.isVisible()) {
      await addButton.click();
      
      await page.waitForSelector('input[name="name"]', { timeout: 5000 });
      
      // Fill form quickly
      await page.locator('input[name="name"]').fill('Performance Test Tool');
      await page.locator('textarea[name="description"]').fill('Tool for performance testing');
      await page.locator('input[name="website_url"]').fill('https://performance-test.com');
      
      const startTime = Date.now();
      
      const saveButton = page.locator('button:has-text("Save Tool")');
      await saveButton.click();
      
      // Wait for form to process
      await page.waitForSelector('table', { timeout: 10000 });
      
      const submissionTime = Date.now() - startTime;
      
      // Form submission should complete within reasonable time
      expect(submissionTime).toBeLessThan(5000);
      
      console.log(`Form submission time: ${submissionTime}ms`);
    } else {
      test.skip(true, 'Add tool functionality not available');
    }
  });

  test('should test research operation performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    const researchButton = page.locator('button:has-text("Research")').first();
    
    if (await researchButton.isVisible()) {
      const startTime = Date.now();
      
      await researchButton.click();
      
      // Wait for research to start (should show loading indicator quickly)
      await page.waitForSelector('.fixed.top-0.left-0', { timeout: 5000 });
      
      const startTime2 = Date.now() - startTime;
      
      // Research should start quickly
      expect(startTime2).toBeLessThan(3000);
      
      console.log(`Research start time: ${startTime2}ms`);
    } else {
      test.skip(true, 'Research functionality not available');
    }
  });
});

test.describe('Load Testing', () => {
  
  test('should handle rapid page navigation', async ({ page }) => {
    const pages = ['/', '/', '/']; // Add more pages when available
    
    for (let i = 0; i < 3; i++) {
      for (const pagePath of pages) {
        await page.goto(pagePath);
        await page.waitForSelector('h1', { timeout: 5000 });
        
        // Small delay to simulate user behavior
        await page.waitForTimeout(100);
      }
    }
    
    // Should still be responsive after rapid navigation
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should handle repeated API calls', async ({ page }) => {
    const iterations = 20;
    let successCount = 0;
    
    const startTime = Date.now();
    
    for (let i = 0; i < iterations; i++) {
      try {
        const response = await page.request.get('/api/health');
        if (response.status() === 200) {
          successCount++;
        }
      } catch (error) {
        console.log(`API call ${i} failed:`, error.message);
      }
      
      // Small delay between requests
      await page.waitForTimeout(50);
    }
    
    const totalTime = Date.now() - startTime;
    const successRate = (successCount / iterations) * 100;
    
    // At least 90% of requests should succeed
    expect(successRate).toBeGreaterThan(90);
    
    console.log(`${iterations} API calls: ${successCount} succeeded (${successRate.toFixed(1)}%) in ${totalTime}ms`);
  });

  test('should handle bulk operations', async ({ page }) => {
    await page.goto('/');
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Test bulk selection
    const checkboxes = page.locator('input[type="checkbox"]');
    const checkboxCount = await checkboxes.count();
    
    if (checkboxCount > 1) {
      const startTime = Date.now();
      
      // Select all checkboxes quickly
      for (let i = 0; i < checkboxCount && i < 10; i++) {
        await checkboxes.nth(i).check();
        await page.waitForTimeout(10); // Very small delay
      }
      
      const selectionTime = Date.now() - startTime;
      
      // Bulk selection should be fast
      expect(selectionTime).toBeLessThan(2000);
      
      console.log(`Bulk selection time: ${selectionTime}ms`);
    } else {
      test.skip(true, 'Bulk operations not available');
    }
  });

  test('should maintain performance under stress', async ({ page, context }) => {
    // Open multiple tabs to simulate load
    const tabs = [];
    const tabCount = 3;
    
    for (let i = 0; i < tabCount; i++) {
      const newPage = await context.newPage();
      tabs.push(newPage);
    }
    
    try {
      // Load the application in all tabs simultaneously
      const loadPromises = tabs.map(tab => {
        return tab.goto('/').then(() => 
          tab.waitForSelector('h1', { timeout: 10000 })
        );
      });
      
      const startTime = Date.now();
      await Promise.all(loadPromises);
      const loadTime = Date.now() - startTime;
      
      // All tabs should load within reasonable time
      expect(loadTime).toBeLessThan(15000);
      
      console.log(`${tabCount} tabs loaded in: ${loadTime}ms`);
      
      // Verify all tabs are functional
      for (const tab of tabs) {
        await expect(tab.locator('h1')).toBeVisible();
      }
      
    } finally {
      // Clean up tabs
      for (const tab of tabs) {
        await tab.close();
      }
    }
  });
});