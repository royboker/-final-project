// @ts-check
import { test, expect } from '@playwright/test';

// ── Landing page ──────────────────────────────────────────────────────────────

test('landing page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Document Analysis Platform|DocuGuard/i);
});

test('landing page has DocuGuard title text', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('.logo-text').first()).toBeVisible();
});

test('landing page has sign in and create account buttons', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('navigation').getByRole('button', { name: 'Sign in' })).toBeVisible();
  await expect(page.getByRole('navigation').getByRole('button', { name: 'Create account' })).toBeVisible();
});

test('landing page sign in button navigates to login', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('navigation').getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});

test('landing page create account button navigates to register', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Create account' }).click();
  await page.waitForURL('**/register');
  await expect(page).toHaveURL(/register/);
});

// ── Protected routes ──────────────────────────────────────────────────────────

test('dashboard redirects to login when not authenticated', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});

test('scan page redirects to login when not authenticated', async ({ page }) => {
  await page.goto('/scan');
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});

test('profile page redirects to login when not authenticated', async ({ page }) => {
  await page.goto('/profile');
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});

test('admin page redirects when not authenticated', async ({ page }) => {
  await page.goto('/admin');
  await expect(page).not.toHaveURL(/admin/);
});

// ── Register ↔ Login navigation ───────────────────────────────────────────────

test('register page has link back to login', async ({ page }) => {
  await page.goto('/register');
  await page.click('text=Sign in');
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});

test('login page has link to register', async ({ page }) => {
  await page.goto('/login');
  await page.click('text=Create one');
  await page.waitForURL('**/register');
  await expect(page).toHaveURL(/register/);
});

test('forgot password page has back to login button', async ({ page }) => {
  await page.goto('/forgot-password');
  await page.click('text=Back to Login');
  await page.waitForURL('**/login');
  await expect(page).toHaveURL(/login/);
});
