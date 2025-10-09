import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load and display dashboard elements', async ({ page }) => {
    await page.goto('/');

    // Check if the main heading is visible
    await expect(page.getByRole('heading', { name: /welcome to engram/i })).toBeVisible();

    // Check if KPI cards are present
    await expect(page.getByText('Total Memories')).toBeVisible();
    await expect(page.getByText('Documents')).toBeVisible();
    await expect(page.getByText('Connections')).toBeVisible();
    await expect(page.getByText('P95 Latency')).toBeVisible();

    // Check if quick actions are present
    await expect(page.getByText('Quick Actions')).toBeVisible();
    await expect(page.getByText('Ingest URL')).toBeVisible();
    await expect(page.getByText('Upload File')).toBeVisible();
    await expect(page.getByText('Open Chat')).toBeVisible();
    await expect(page.getByText('Explore Graph')).toBeVisible();
  });

  test('should navigate to ingest page from quick actions', async ({ page }) => {
    await page.goto('/');

    // Click on "Ingest URL" quick action
    await page.getByText('Ingest URL').click();

    // Should navigate to ingest page
    await expect(page).toHaveURL(/.*\/ingest/);
    await expect(page.getByRole('heading', { name: /ingest content/i })).toBeVisible();
  });

  test('should navigate to chat page from quick actions', async ({ page }) => {
    await page.goto('/');

    // Click on "Open Chat" quick action
    await page.getByText('Open Chat').click();

    // Should navigate to chat page
    await expect(page).toHaveURL(/.*\/chat/);
    await expect(page.getByRole('heading', { name: /chat with memories/i })).toBeVisible();
  });
});
