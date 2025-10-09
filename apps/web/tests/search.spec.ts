import { test, expect } from '@playwright/test';

test.describe('Search', () => {
  test('should load search page', async ({ page }) => {
    await page.goto('/search');

    // Check if the main heading is visible
    await expect(page.getByRole('heading', { name: /search memories/i })).toBeVisible();

    // Check if search bar is present
    await expect(page.getByPlaceholder(/search memories/i)).toBeVisible();

    // Check if filters button is present
    await expect(page.getByRole('button', { name: /filters/i })).toBeVisible();
  });

  test('should perform search', async ({ page }) => {
    await page.goto('/search');

    // Type in search box
    const searchInput = page.getByPlaceholder(/search memories/i);
    await searchInput.fill('machine learning');

    // Press Enter to search
    await searchInput.press('Enter');

    // Should show search results or empty state
    await expect(page.getByText(/found \d+ memories|no memories found/i)).toBeVisible();
  });

  test('should toggle filters panel', async ({ page }) => {
    await page.goto('/search');

    // Click filters button
    await page.getByRole('button', { name: /filters/i }).click();

    // Check if filters panel is visible
    await expect(page.getByText(/content types/i)).toBeVisible();
    await expect(page.getByText(/minimum importance/i)).toBeVisible();
  });

  test('should use keyboard shortcut for search', async ({ page }) => {
    await page.goto('/');

    // Press Cmd+K (or Ctrl+K on Windows/Linux)
    await page.keyboard.press('Meta+k');

    // Should navigate to search page
    await expect(page).toHaveURL(/.*\/search/);
  });
});
