// Run against a local editor server with PLAYWRIGHT_MODULE set when Playwright is not on NODE_PATH.
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function main() {
    const browser = await chromium.launch({
        headless: true,
        ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
    });
    try {
        const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
        page.setDefaultTimeout(60000);
        const errors = [];
        page.on('pageerror', (error) => errors.push(error.message));
        let initialDetailCalls = 0;
        await page.route('**/api/wonder-localization/wonders/*', async (route) => {
            if (route.request().method() === 'GET' && initialDetailCalls++ === 0) {
                await route.fulfill({ status: 503, json: { detail: 'test detail failure' } });
            } else {
                await route.continue();
            }
        });

        let catalogCalls = 0;
        let releaseCatalog;
        let releaseStaleCatalog;
        let staleStarted;
        const catalogGate = new Promise((resolve) => { releaseCatalog = resolve; });
        const staleCatalogGate = new Promise((resolve) => { releaseStaleCatalog = resolve; });
        const staleRequest = new Promise((resolve) => { staleStarted = resolve; });
        await page.route('**/api/wonder-localization/ritual-designs', async (route) => {
            catalogCalls += 1;
            if (catalogCalls === 1) {
                await route.fulfill({ status: 503, json: { detail: 'test catalog failure' } });
            } else if (catalogCalls === 2) {
                await catalogGate;
                await route.continue();
            } else if (catalogCalls === 3) {
                staleStarted();
                const response = await route.fetch();
                const payload = await response.json();
                await staleCatalogGate;
                await route.fulfill({ response, json: { ...payload, count: 999 } });
            } else {
                await route.continue();
            }
        });
        let itemCalls = 0;
        await page.route('**/api/wonder-localization/ritual-designs/*', async (route) => {
            if (itemCalls++ === 0) {
                await route.fulfill({ status: 500, json: { detail: 'test item failure' } });
            } else {
                await route.continue();
            }
        });

        await page.goto(process.env.EDITOR_URL || 'http://127.0.0.1:8760/', { waitUntil: 'domcontentloaded' });
        await page.locator('.tool-hub-tab-btn[data-tool="wonder-localization"]').click();
        await page.locator('#wonder-list .wonder-item').first().waitFor();
        await page.getByText('test detail failure', { exact: false }).first().waitFor();
        assert.equal(catalogCalls, 0);
        await page.locator('#wonder-list .wonder-item').first().click();
        await page.locator('#language-tabs button').first().waitFor();
        await page.locator('#wonder-kind-tabs button').nth(1).click();
        await page.locator('#wonder-list .wonder-item').first().click();
        const ritualTab = page.locator('#language-tabs button').filter({ hasText: '仪式设计' });
        await ritualTab.waitFor();
        assert.equal(catalogCalls, 0);
        await ritualTab.click();
        const panel = page.locator('[data-editor-tab="ritual-design"]');
        await panel.getByText('test catalog failure', { exact: false }).waitFor();
        assert(await panel.locator('.ritual-design-current').getByText('历史氛围').first().isVisible());
        const prompt = panel.locator('[data-ritual-prompt-input]');
        await panel.getByRole('button', { name: '用当前设计生成 Prompt 草稿' }).click();
        assert((await prompt.inputValue()).includes('历史氛围:'));

        await prompt.fill('draft while catalog loads');
        await panel.getByRole('button', { name: '重试' }).click();
        await page.waitForFunction(() => document.querySelector('.ritual-design-catalog-content .empty-state')?.textContent.includes('正在加载'));
        await prompt.focus();
        await prompt.evaluate((element) => element.setSelectionRange(6, 6));
        const originalInput = await prompt.elementHandle();
        releaseCatalog();
        await panel.locator('.ritual-design-all').waitFor();
        assert.equal(await prompt.inputValue(), 'draft while catalog loads');
        assert(await prompt.evaluate((element) => element === document.activeElement && element.selectionStart === 6));
        assert(await originalInput.evaluate((element) => element === document.activeElement));

        const other = panel.locator('.ritual-design-all details.ritual-design-card').nth(1);
        await other.locator(':scope > summary').click();
        await other.getByText('test item failure', { exact: false }).waitFor();
        await other.locator(':scope > summary').click();
        await other.locator(':scope > summary').click();
        await other.locator(':scope > .ritual-design-body').waitFor();
        assert.equal(itemCalls, 2);

        await page.locator('#reload-button').click();
        await staleRequest;
        await page.waitForFunction(() => document.querySelector('.tool-wonder-localization').dataset.busy === 'false');
        await page.locator('#reload-button').click();
        await panel.locator('.ritual-design-all').waitFor();
        const staleResponse = page.waitForResponse((response) => response.url().endsWith('/api/wonder-localization/ritual-designs')
            && response.status() === 200);
        releaseStaleCatalog();
        await staleResponse;
        assert(!(await panel.locator('.ritual-design-count').textContent()).includes('999'));

        await page.setViewportSize({ width: 390, height: 844 });
        assert(await prompt.isVisible());
        assert(await panel.locator('.origin-pill').evaluate((element) => element.scrollWidth <= element.clientWidth + 1));
        assert.deepEqual(errors, []);
        console.log('Wonder browser regression passed');
    } finally {
        await browser.close();
    }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
