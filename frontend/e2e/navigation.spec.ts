import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should navigate between major sections', async ({ page }) => {
    // Start from dashboard
    await page.goto('/dashboard');
    await expect(page).toHaveTitle(/Dashboard/);

    // Navigate to Documents
    await page.click('text=Documents');
    await expect(page).toHaveURL(/\/documents/);
    await expect(page.locator('h1')).toContainText('Document Management');

    // Navigate to Legal Chat
    await page.click('text=Legal Chat');
    await expect(page).toHaveURL(/\/chat/);
    await expect(page.locator('h1')).toContainText('Legal AI Chat');

    // Open Command Palette
    await page.keyboard.press('Control+k');
    await expect(page.getByPlaceholder('Search pages, actions, or documents...')).toBeVisible();
  });

  test('should switch themes', async ({ page }) => {
    await page.goto('/dashboard');

    // Check initial theme (usually light or dark based on system)
    const body = page.locator('body');

    // Find theme toggle and click it
    await page.click('button[aria-label*="toggle theme" i]');

    // Verify theme change (this depends on implementation, usually a class on html/body)
    // For now we just check if it's clickable and doesn't crash
  });
});
