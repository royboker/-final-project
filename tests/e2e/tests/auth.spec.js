// @ts-check
import { test, expect } from '@playwright/test';

function uniqueEmail() {
  return `e2e_${Date.now()}@pytest.com`;
}

// ── Register page ─────────────────────────────────────────────────────────────

test('register page renders', async ({ page }) => {
  await page.goto('/register');
  await expect(page.locator('h1')).toContainText('Create account');
  await expect(page.locator('#name')).toBeVisible();
  await expect(page.locator('#email')).toBeVisible();
  await expect(page.locator('#password')).toBeVisible();
  await expect(page.locator('#confirm')).toBeVisible();
});

test('register shows error when fields are empty', async ({ page }) => {
  await page.goto('/register');
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('Please fill in all fields');
});

test('register shows error when passwords do not match', async ({ page }) => {
  await page.goto('/register');
  await page.fill('#name', 'Test User');
  await page.fill('#email', uniqueEmail());
  await page.fill('#password', 'Password123');
  await page.fill('#confirm', 'DifferentPass1');
  // no need to check terms — password mismatch is validated before terms
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('Passwords do not match');
});

test('register shows error when password too short', async ({ page }) => {
  await page.goto('/register');
  await page.fill('#name', 'Test User');
  await page.fill('#email', uniqueEmail());
  await page.fill('#password', 'abc');
  await page.fill('#confirm', 'abc');
  // no need to check terms — length is validated before terms
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('8 characters');
});

test('register shows error when terms not accepted', async ({ page }) => {
  await page.goto('/register');
  await page.fill('#name', 'Test User');
  await page.fill('#email', uniqueEmail());
  await page.fill('#password', 'Password123');
  await page.fill('#confirm', 'Password123');
  // terms checkbox NOT checked
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('terms');
});

test('register success redirects to check-email', async ({ page }) => {
  await page.goto('/register');
  await page.fill('#name', 'E2E User');
  await page.fill('#email', uniqueEmail());
  await page.fill('#password', 'Password123');
  await page.fill('#confirm', 'Password123');
  await page.locator('.auth-check-box').click();
  await page.click('button[type="submit"]');
  await page.waitForURL('**/check-email', { timeout: 10_000 });
  await expect(page).toHaveURL(/check-email/);
});

// ── Login page ────────────────────────────────────────────────────────────────

test('login page renders', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('h1')).toContainText('Welcome back');
  await expect(page.locator('#email')).toBeVisible();
  await expect(page.locator('#password')).toBeVisible();
});

test('login shows error when fields are empty', async ({ page }) => {
  await page.goto('/login');
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('Please fill in all fields');
});

test('login shows error with wrong credentials', async ({ page }) => {
  await page.goto('/login');
  await page.fill('#email', 'nonexistent@example.com');
  await page.fill('#password', 'WrongPassword1');
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toBeVisible({ timeout: 10_000 });
});

test('login page has link to register', async ({ page }) => {
  await page.goto('/login');
  await page.click('text=Create one');
  await page.waitForURL('**/register');
  await expect(page).toHaveURL(/register/);
});

test('login page has forgot password link', async ({ page }) => {
  await page.goto('/login');
  await page.click('text=Forgot password?');
  await page.waitForURL('**/forgot-password');
  await expect(page).toHaveURL(/forgot-password/);
});

// ── Forgot password page ──────────────────────────────────────────────────────

test('forgot password page renders', async ({ page }) => {
  await page.goto('/forgot-password');
  await expect(page.locator('h2')).toContainText('Forgot password');
  await expect(page.locator('#email')).toBeVisible();
});

test('forgot password shows error when email is empty', async ({ page }) => {
  await page.goto('/forgot-password');
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('email');
});

test('forgot password shows error for invalid email format', async ({ page }) => {
  await page.goto('/forgot-password');
  await page.fill('#email', 'notanemail');
  await page.click('button[type="submit"]');
  await expect(page.locator('.auth-error')).toContainText('valid email');
});

test('forgot password shows success state after submit', async ({ page }) => {
  await page.goto('/forgot-password');
  await page.fill('#email', 'anyone@example.com');
  await page.click('button[type="submit"]');
  await expect(page.locator('h2')).toContainText('Check your email', { timeout: 10_000 });
});
