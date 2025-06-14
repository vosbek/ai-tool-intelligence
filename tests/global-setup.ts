// global-setup.ts - Global setup for Playwright tests

import { chromium, FullConfig } from '@playwright/test';
import path from 'path';
import fs from 'fs';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up global test environment...');

  // Create necessary directories
  const authDir = path.join(__dirname, 'playwright', '.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  // Wait for backend to be ready
  console.log('⏳ Waiting for backend to be ready...');
  await waitForBackend();

  // Wait for frontend to be ready
  console.log('⏳ Waiting for frontend to be ready...');
  await waitForFrontend();

  console.log('✅ Global setup complete');
}

async function waitForBackend(maxWaitTime = 60000) {
  const startTime = Date.now();
  const backendUrl = 'http://localhost:5000/api/health';
  
  while (Date.now() - startTime < maxWaitTime) {
    try {
      const response = await fetch(backendUrl);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'healthy') {
          console.log('✅ Backend is ready');
          return;
        }
      }
    } catch (error) {
      // Backend not ready yet, continue waiting
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('Backend failed to start within timeout');
}

async function waitForFrontend(maxWaitTime = 60000) {
  const startTime = Date.now();
  const frontendUrl = 'http://localhost:3000';
  
  while (Date.now() - startTime < maxWaitTime) {
    try {
      const response = await fetch(frontendUrl);
      if (response.ok) {
        console.log('✅ Frontend is ready');
        return;
      }
    } catch (error) {
      // Frontend not ready yet, continue waiting
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error('Frontend failed to start within timeout');
}

export default globalSetup;