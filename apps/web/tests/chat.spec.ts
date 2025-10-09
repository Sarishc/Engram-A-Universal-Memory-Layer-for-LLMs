import { test, expect } from '@playwright/test';

test.describe('Chat', () => {
  test('should load chat page', async ({ page }) => {
    await page.goto('/chat');

    // Check if the main heading is visible
    await expect(page.getByRole('heading', { name: /chat with memories/i })).toBeVisible();

    // Check if chat input is present
    await expect(page.getByPlaceholder(/ask about your memories/i)).toBeVisible();

    // Check if send button is present
    await expect(page.getByRole('button', { name: /send/i })).toBeVisible();
  });

  test('should send a message', async ({ page }) => {
    await page.goto('/chat');

    // Type a message
    const messageInput = page.getByPlaceholder(/ask about your memories/i);
    await messageInput.fill('What is machine learning?');

    // Send message
    await page.getByRole('button', { name: /send/i }).click();

    // Should show the user message
    await expect(page.getByText('What is machine learning?')).toBeVisible();

    // Should show loading or response
    await expect(page.getByText(/thinking|loading/i)).toBeVisible();
  });

  test('should use keyboard shortcut to send message', async ({ page }) => {
    await page.goto('/chat');

    // Type a message
    const messageInput = page.getByPlaceholder(/ask about your memories/i);
    await messageInput.fill('Hello world');

    // Press Enter to send
    await messageInput.press('Enter');

    // Should show the user message
    await expect(page.getByText('Hello world')).toBeVisible();
  });

  test('should toggle chat settings', async ({ page }) => {
    await page.goto('/chat');

    // Click settings button
    await page.getByRole('button', { name: /settings/i }).click();

    // Check if settings panel is visible
    await expect(page.getByText(/memory count/i)).toBeVisible();
    await expect(page.getByText(/modalities/i)).toBeVisible();
    await expect(page.getByText(/require grounding/i)).toBeVisible();
  });

  test('should create new chat session', async ({ page }) => {
    await page.goto('/chat');

    // Click new chat button
    await page.getByRole('button', { name: /new chat/i }).click();

    // Should show success message
    await expect(page.getByText(/new chat started/i)).toBeVisible();
  });
});
