// e2e/auth.setup.ts - Authentication setup for Playwright tests

import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../playwright/.auth/user.json');

setup('authenticate', async ({ page }) => {
  // For this application, we don't have authentication yet
  // But we'll prepare the auth state file anyway for future use
  
  // Navigate to the application
  await page.goto('/');
  
  // Wait for the application to load
  await page.waitForSelector('h1:has-text("AI Tool Intelligence Platform")', { timeout: 10000 });
  
  // Verify we can see the main interface
  await expect(page.locator('h1')).toContainText('AI Tool Intelligence Platform');
  
  // Save signed-in state to reuse in other tests
  await page.context().storageState({ path: authFile });
});