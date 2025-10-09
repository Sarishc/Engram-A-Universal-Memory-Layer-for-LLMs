import { test, expect } from '@playwright/test';

test.describe('Ingest', () => {
  test('should load ingest page', async ({ page }) => {
    await page.goto('/ingest');

    // Check if the main heading is visible
    await expect(page.getByRole('heading', { name: /ingest content/i })).toBeVisible();

    // Check if tabs are present
    await expect(page.getByRole('tab', { name: /url/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /file/i })).toBeVisible();
    await expect(page.getByRole('tab', { name: /chat/i })).toBeVisible();
  });

  test('should switch between ingest tabs', async ({ page }) => {
    await page.goto('/ingest');

    // Click on File tab
    await page.getByRole('tab', { name: /file/i }).click();
    await expect(page.getByText(/upload files/i)).toBeVisible();

    // Click on Chat tab
    await page.getByRole('tab', { name: /chat/i }).click();
    await expect(page.getByText(/ingest chat messages/i)).toBeVisible();

    // Click back to URL tab
    await page.getByRole('tab', { name: /url/i }).click();
    await expect(page.getByText(/ingest from url/i)).toBeVisible();
  });

  test('should validate URL form', async ({ page }) => {
    await page.goto('/ingest');

    // Try to submit without URL
    await page.getByRole('button', { name: /start ingestion/i }).click();

    // Should show validation error
    await expect(page.getByText(/please enter a valid url/i)).toBeVisible();
  });

  test('should submit URL form with valid data', async ({ page }) => {
    await page.goto('/ingest');

    // Fill in URL
    await page.getByPlaceholder(/https:\/\/example.com\/article/i).fill('https://example.com/article');

    // Select content type
    await page.getByText(/web page/i).click();

    // Submit form
    await page.getByRole('button', { name: /start ingestion/i }).click();

    // Should show success message or loading state
    await expect(page.getByText(/ingestion job started|starting ingestion/i)).toBeVisible();
  });
});
