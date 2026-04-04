/**
 * Script de génération automatique de screenshots pour la documentation
 * 
 * Usage:
 *   npx tsx scripts/generate_screenshots.ts
 * 
 * Prérequis:
 *   - npm install -D @playwright/test tsx
 *   - npm install -D @types/node
 *   - Backend démarré sur http://localhost:8000
 *   - Frontend démarré sur http://localhost:3000
 */

import { chromium, type Browser, type Page } from '@playwright/test';
import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const SCREENSHOTS_DIR = join(process.cwd(), 'docs', 'user-guide', 'screenshots');
const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// Credentials de test (remplacez par vos propres credentials de test)
const TEST_USER = {
  email: process.env.TEST_EMAIL || 'demo@assistant-matanne.fr',
  password: process.env.TEST_PASSWORD || 'demo123456',
};

interface Screenshot {
  name: string;
  path: string;
  action?: (page: Page) => Promise<void>;
  waitFor?: number;
}

const SCREENSHOTS: Screenshot[] = [
  {
    name: '01-landing',
    path: '/',
    waitFor: 1000,
  },
  {
    name: '02-login',
    path: '/connexion',
    waitFor: 500,
  },
  {
    name: '03-dashboard',
    path: '/',
    action: async (page) => {
      await login(page);
    },
    waitFor: 2000,
  },
  {
    name: '04-cuisine-recettes',
    path: '/cuisine/recettes',
    waitFor: 1500,
  },
  {
    name: '05-cuisine-planning',
    path: '/cuisine/planning',
    waitFor: 1500,
  },
  {
    name: '06-cuisine-courses',
    path: '/cuisine/courses',
    waitFor: 1500,
  },
  {
    name: '07-cuisine-inventaire',
    path: '/cuisine/inventaire',
    waitFor: 1500,
  },
  {
    name: '08-famille-jules',
    path: '/famille/jules',
    waitFor: 1500,
  },
  {
    name: '09-famille-activites',
    path: '/famille/activites',
    waitFor: 1500,
  },
  {
    name: '10-famille-weekend',
    path: '/famille/weekend',
    waitFor: 1500,
  },
  {
    name: '11-famille-budget',
    path: '/famille/budget',
    waitFor: 1500,
  },
  {
    name: '12-maison-projets',
    path: '/maison/projets',
    waitFor: 1500,
  },
  {
    name: '13-maison-jardin',
    path: '/maison/jardin',
    waitFor: 1500,
  },
  {
    name: '14-maison-energie',
    path: '/maison/energie',
    waitFor: 1500,
  },
  {
    name: '15-maison-visualisation',
    path: '/maison/visualisation',
    waitFor: 1500,
  },
  {
    name: '16-jeux-paris',
    path: '/jeux/paris',
    waitFor: 1500,
  },
  {
    name: '17-outils-chat-ia',
    path: '/outils/chat-ia',
    waitFor: 1500,
  },
  {
    name: '18-planning-timeline',
    path: '/planning/timeline',
    waitFor: 1500,
  },
];

/**
 * Login helper
 */
async function login(page: Page): Promise<void> {
  console.log('🔐 Logging in...');
  
  await page.goto(`${BASE_URL}/connexion`);
  await page.fill('input[type="email"]', TEST_USER.email);
  await page.fill('input[type="password"]', TEST_USER.password);
  await page.click('button[type="submit"]');
  
  // Wait for redirect to dashboard
  await page.waitForURL(`${BASE_URL}/`, { timeout: 5000 });
  console.log('✅ Logged in successfully');
}

/**
 * Take a screenshot with error handling
 */
async function takeScreenshot(
  page: Page,
  browser: Browser,
  screenshot: Screenshot
): Promise<void> {
  const fullPath = join(SCREENSHOTS_DIR, `${screenshot.name}.png`);
  
  try {
    console.log(`📸 Capturing: ${screenshot.name}`);
    
    // Navigate to page
    await page.goto(`${BASE_URL}${screenshot.path}`, {
      waitUntil: 'networkidle',
      timeout: 10000,
    });
    
    // Execute custom action if defined
    if (screenshot.action) {
      await screenshot.action(page);
    }
    
    // Wait for page to settle
    if (screenshot.waitFor) {
      await page.waitForTimeout(screenshot.waitFor);
    }
    
    // Take screenshot
    await page.screenshot({
      path: fullPath,
      fullPage: false, // Capture viewport only (fold)
    });
    
    console.log(`✅ Saved: ${screenshot.name}.png`);
  } catch (error) {
    console.error(`❌ Failed: ${screenshot.name}`, error);
  }
}

/**
 * Main function
 */
async function main() {
  console.log('🚀 Generating screenshots for documentation...\n');
  
  // Create screenshots directory if it doesn't exist
  if (!existsSync(SCREENSHOTS_DIR)) {
    mkdirSync(SCREENSHOTS_DIR, { recursive: true });
    console.log(`📁 Created directory: ${SCREENSHOTS_DIR}\n`);
  }
  
  // Launch browser
  const browser = await chromium.launch({
    headless: true, // Set to false for debugging
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });
  
  const page = await context.newPage();
  
  // Login once (credentials persist in context)
  await login(page);
  
  // Take screenshots
  for (const screenshot of SCREENSHOTS) {
    await takeScreenshot(page, browser, screenshot);
  }
  
  // Cleanup
  await browser.close();
  
  console.log(`\n✨ Done! Generated ${SCREENSHOTS.length} screenshots in ${SCREENSHOTS_DIR}`);
}

// Run
main().catch((error) => {
  console.error('💥 Fatal error:', error);
  process.exit(1);
});
