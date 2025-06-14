// global-teardown.ts - Global teardown for Playwright tests

import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Running global teardown...');
  
  // Any cleanup operations can be added here
  // For now, we let the web servers stop naturally when the process ends
  
  console.log('✅ Global teardown complete');
}

export default globalTeardown;