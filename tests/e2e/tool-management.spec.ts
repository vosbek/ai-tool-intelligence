// e2e/tool-management.spec.ts - End-to-end tests for tool management

import { test, expect, Page } from '@playwright/test';

test.describe('Tool Management', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
  });

  test('should display the main dashboard', async ({ page }) => {
    // Check that main elements are visible
    await expect(page.locator('h1')).toContainText('AI Tool Intelligence Platform');
    await expect(page.locator('p')).toContainText('Comprehensive research and analysis of AI developer tools');
    
    // Check for the "Add New Tool" button
    await expect(page.locator('button:has-text("Add New Tool")')).toBeVisible();
    
    // Check for summary stats
    await expect(page.locator('text=Total Tools')).toBeVisible();
    await expect(page.locator('text=Researched')).toBeVisible();
    await expect(page.locator('text=Processing')).toBeVisible();
    await expect(page.locator('text=Categories')).toBeVisible();
  });

  test('should display tools table', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check table headers
    await expect(page.locator('th:has-text("Tool")')).toBeVisible();
    await expect(page.locator('th:has-text("Category")')).toBeVisible();
    await expect(page.locator('th:has-text("Status")')).toBeVisible();
    await expect(page.locator('th:has-text("Pricing")')).toBeVisible();
    await expect(page.locator('th:has-text("Last Updated")')).toBeVisible();
    await expect(page.locator('th:has-text("Actions")')).toBeVisible();
    
    // Check that tools are displayed
    const toolRows = page.locator('tbody tr');
    await expect(toolRows).toHaveCount(5); // Should have 5 sample tools
  });

  test('should filter tools by category', async ({ page }) => {
    // Wait for tools table and filters to load
    await page.waitForSelector('table', { timeout: 10000 });
    await page.waitForSelector('select[value=""]', { timeout: 5000 });
    
    // Get initial tool count
    const initialRows = await page.locator('tbody tr').count();
    
    // Filter by a specific category (e.g., "Code Assistants")
    await page.selectOption('select', { label: 'Code Assistants' });
    
    // Wait for filter to apply
    await page.waitForTimeout(500);
    
    // Check that fewer tools are displayed
    const filteredRows = await page.locator('tbody tr').count();
    expect(filteredRows).toBeLessThanOrEqual(initialRows);
    
    // Clear filter
    await page.selectOption('select', '');
    await page.waitForTimeout(500);
    
    // Should show all tools again
    const resetRows = await page.locator('tbody tr').count();
    expect(resetRows).toBe(initialRows);
  });

  test('should filter tools by status', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Filter by completed status
    const statusSelect = page.locator('select').nth(1); // Second select is for status
    await statusSelect.selectOption('completed');
    
    // Wait for filter to apply
    await page.waitForTimeout(500);
    
    // Check that only completed tools are shown
    const statusBadges = page.locator('.bg-green-500'); // Completed status badge
    const visibleRows = page.locator('tbody tr');
    const rowCount = await visibleRows.count();
    
    if (rowCount > 0) {
      // All visible tools should have completed status
      await expect(statusBadges).toHaveCount(rowCount);
    }
  });

  test('should search tools by name', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Search for a specific tool
    const searchInput = page.locator('input[placeholder="Search tools..."]');
    await searchInput.fill('Cursor');
    
    // Wait for search to apply
    await page.waitForTimeout(500);
    
    // Should show only matching tools
    const visibleRows = page.locator('tbody tr');
    const rowCount = await visibleRows.count();
    
    if (rowCount > 0) {
      // All visible tools should contain "Cursor" in the name
      for (let i = 0; i < rowCount; i++) {
        const row = visibleRows.nth(i);
        await expect(row.locator('td').first()).toContainText('Cursor', { ignoreCase: true });
      }
    }
    
    // Clear search
    await searchInput.clear();
    await page.waitForTimeout(500);
  });

  test('should open tool details', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click on the first "View" button
    await page.locator('button:has-text("View")').first().click();
    
    // Should navigate to tool detail view
    await expect(page.locator('h2')).toBeVisible();
    await expect(page.locator('button:has-text("Edit")')).toBeVisible();
    await expect(page.locator('button:has-text("Research")')).toBeVisible();
    await expect(page.locator('button:has-text("Close")')).toBeVisible();
    
    // Check for tool information sections
    await expect(page.locator('h3:has-text("Basic Information")')).toBeVisible();
    await expect(page.locator('h3:has-text("URLs")')).toBeVisible();
    await expect(page.locator('h3:has-text("Processing Information")')).toBeVisible();
  });

  test('should open add tool form', async ({ page }) => {
    // Click "Add New Tool" button
    await page.locator('button:has-text("Add New Tool")').click();
    
    // Should show the tool form
    await expect(page.locator('h2:has-text("Add New Tool")')).toBeVisible();
    
    // Check for form fields
    await expect(page.locator('input[name="name"]')).toBeVisible();
    await expect(page.locator('select[name="category_id"]')).toBeVisible();
    await expect(page.locator('textarea[name="description"]')).toBeVisible();
    await expect(page.locator('input[name="website_url"]')).toBeVisible();
    await expect(page.locator('input[name="github_url"]')).toBeVisible();
    
    // Check for action buttons
    await expect(page.locator('button:has-text("Save Tool")')).toBeVisible();
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
  });

  test('should create a new tool', async ({ page }) => {
    // Click "Add New Tool" button
    await page.locator('button:has-text("Add New Tool")').click();
    
    // Fill out the form
    await page.locator('input[name="name"]').fill('Test E2E Tool');
    await page.locator('select[name="category_id"]').selectOption('4'); // Code Assistants
    await page.locator('textarea[name="description"]').fill('A test tool created by E2E tests');
    await page.locator('input[name="website_url"]').fill('https://test-e2e-tool.com');
    await page.locator('input[name="github_url"]').fill('https://github.com/test/e2e-tool');
    await page.locator('select[name="pricing_model"]').selectOption('freemium');
    
    // Submit the form
    await page.locator('button:has-text("Save Tool")').click();
    
    // Should return to main view and show the new tool
    await page.waitForSelector('table', { timeout: 10000 });
    await expect(page.locator('td:has-text("Test E2E Tool")')).toBeVisible();
  });

  test('should edit an existing tool', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click on the first "Edit" button
    await page.locator('button:has-text("Edit")').first().click();
    
    // Should show the edit form
    await expect(page.locator('h2:has-text("Edit Tool")')).toBeVisible();
    
    // Modify the description
    const descriptionField = page.locator('textarea[name="description"]');
    await descriptionField.clear();
    await descriptionField.fill('Updated description from E2E test');
    
    // Add internal notes
    await page.locator('textarea[name="internal_notes"]').fill('E2E test notes');
    
    // Submit the form
    await page.locator('button:has-text("Save Tool")').click();
    
    // Should return to main view
    await page.waitForSelector('table', { timeout: 10000 });
  });

  test('should test research functionality', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click on the first "View" button to see tool details
    await page.locator('button:has-text("View")').first().click();
    
    // Click the Research button
    await page.locator('button:has-text("Research")').click();
    
    // Should show progress indicator
    await expect(page.locator('.fixed.top-0.left-0')).toBeVisible();
    
    // Wait for research to complete (should show error since Strands packages aren't available)
    await page.waitForSelector('.bg-red-50', { timeout: 30000 });
    
    // Should show error message about Strands packages
    await expect(page.locator('text=Error:')).toBeVisible();
    await expect(page.locator('text=Strands Agents not available')).toBeVisible();
  });

  test('should handle bulk operations', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Select multiple tools
    const checkboxes = page.locator('input[type="checkbox"]');
    await checkboxes.nth(1).check(); // First tool checkbox (0 is select all)
    await checkboxes.nth(2).check(); // Second tool checkbox
    
    // Should show bulk action button
    await expect(page.locator('button:has-text("Research Selected")')).toBeVisible();
    await expect(page.locator('button:has-text("Clear Selection")')).toBeVisible();
    
    // Test select all functionality
    await checkboxes.nth(0).check(); // Select all checkbox
    
    // All tool checkboxes should be checked
    const toolCheckboxes = await checkboxes.count();
    for (let i = 1; i < toolCheckboxes; i++) {
      await expect(checkboxes.nth(i)).toBeChecked();
    }
    
    // Clear selection
    await page.locator('button:has-text("Clear Selection")').click();
    
    // Checkboxes should be unchecked
    for (let i = 0; i < toolCheckboxes; i++) {
      await expect(checkboxes.nth(i)).not.toBeChecked();
    }
  });

  test('should display notifications', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Trigger an action that creates a notification (like research)
    await page.locator('button:has-text("Research")').first().click();
    
    // Should show notification
    await expect(page.locator('.fixed.top-4.right-4')).toBeVisible();
    
    // Notification should auto-dismiss after 5 seconds or can be manually closed
    const notification = page.locator('.fixed.top-4.right-4');
    if (await notification.isVisible()) {
      // Try to close manually
      await page.locator('button:has-text("✕")').click();
      await expect(notification).not.toBeVisible();
    }
  });

  test('should display research queue', async ({ page }) => {
    // Wait for tools table to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Start a research operation
    await page.locator('button:has-text("Research")').first().click();
    
    // Should show research queue indicator
    await expect(page.locator('.fixed.bottom-4.right-4')).toBeVisible();
    await expect(page.locator('h3:has-text("Research Queue")')).toBeVisible();
    
    // Should show processing item
    await expect(page.locator('text=Processing:')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'This test only runs on mobile');
    
    // Check that the interface adapts to mobile
    await expect(page.locator('h1')).toBeVisible();
    
    // Table should be scrollable on mobile
    const table = page.locator('table');
    await expect(table).toBeVisible();
    
    // Buttons should be accessible
    await expect(page.locator('button:has-text("Add New Tool")')).toBeVisible();
  });

  test('should handle loading states', async ({ page }) => {
    // Intercept API calls to simulate slow responses
    await page.route('**/api/tools', async route => {
      await page.waitForTimeout(2000); // Simulate slow API
      route.continue();
    });
    
    // Navigate to the page
    await page.goto('/');
    
    // Should show loading indicator
    await expect(page.locator('.animate-spin')).toBeVisible();
    await expect(page.locator('text=Loading AI Tool Intelligence Platform...')).toBeVisible();
    
    // Wait for content to load
    await page.waitForSelector('table', { timeout: 15000 });
    
    // Loading indicator should disappear
    await expect(page.locator('text=Loading AI Tool Intelligence Platform...')).not.toBeVisible();
  });

  test('should handle error states', async ({ page }) => {
    // Intercept API calls to simulate errors
    await page.route('**/api/tools', async route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Navigate to the page
    await page.goto('/');
    
    // Should show error state
    await expect(page.locator('text=Error')).toBeVisible();
    await expect(page.locator('text=Failed to load data')).toBeVisible();
    await expect(page.locator('button:has-text("Retry")')).toBeVisible();
    
    // Remove the route override and test retry
    await page.unroute('**/api/tools');
    await page.locator('button:has-text("Retry")').click();
    
    // Should recover and show normal content
    await page.waitForSelector('table', { timeout: 10000 });
  });
});