// Run against a local editor server with PLAYWRIGHT_MODULE set when Playwright is not on NODE_PATH.
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

async function optionCount(select) {
    await select.locator('.option-open-button').click();
    const count = await select.locator('.option-item').count();
    await select.locator('.option-open-button').click();
    return count;
}

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
        let optionCatalogCalls = 0;
        await page.route('**/api/wonder-localization/catalog', async (route) => {
            optionCatalogCalls += 1;
            await route.continue();
        });
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
        assert.equal(optionCatalogCalls, 1);
        assert(await page.locator('#dirty-badge').isHidden());
        await page.locator('#wonder-kind-tabs button').nth(1).click();
        await page.locator('#wonder-list .wonder-item').first().click();
        await page.locator('#wonder-list .wonder-item.active').waitFor();
        assert.equal(optionCatalogCalls, 1);
        assert(await page.locator('#dirty-badge').isHidden());

        const trinityKey = 'unique_trinity_lavra';
        const trinity = page.locator(`#wonder-list .wonder-item[data-wonder-key="${trinityKey}"]`);
        const waitForActive = (key) => page.locator(`#wonder-list .wonder-item.active[data-wonder-key="${key}"]`).waitFor();
        await trinity.click();
        await waitForActive(trinityKey);
        await page.locator('#language-tabs button').filter({ hasText: 'Mechanics' }).click();
        const mechanics = page.locator('[data-editor-tab="mechanics"]');
        const ritual = mechanics.locator('.field-card:has(input[data-field-type="unique_ritual_editor"])');
        const ceremony = mechanics.locator('.field-card:has(input[data-field-type="unique_ceremony_editor"])');
        const ritualKey = ritual.locator('.scalar-grid').first().locator('label.scalar-field').first().locator('input');
        const modeSelect = ritual.locator('.scalar-grid').first().locator('label.scalar-field').nth(1).locator('.option-combobox');
        const stageCostSelect = ceremony.locator('[data-row-list="stage-cost"]').first()
            .locator('.structured-row .option-combobox').first();
        const originalKey = await ritualKey.inputValue();
        const modeOptions = await optionCount(modeSelect);
        const stageCostOptions = await optionCount(stageCostSelect);
        assert(modeOptions > 1);
        assert(stageCostOptions > 1);
        await ritualKey.fill(`${originalKey}_draft_probe`);
        assert(await page.locator('#dirty-badge').isVisible());
        const otherWonder = page.locator('#wonder-list .wonder-item:not(.active)').first();
        const otherKey = await otherWonder.getAttribute('data-wonder-key');
        await otherWonder.click();
        await waitForActive(otherKey);
        await trinity.click();
        await waitForActive(trinityKey);
        assert.equal(await ritualKey.inputValue(), `${originalKey}_draft_probe`);
        assert(await page.locator('#dirty-badge').isVisible());
        assert.equal(await optionCount(modeSelect), modeOptions);
        assert.equal(await optionCount(stageCostSelect), stageCostOptions);
        await ritualKey.fill(originalKey);
        assert(await page.locator('#dirty-badge').isHidden());
        assert.equal(optionCatalogCalls, 1);

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
        assert.equal(optionCatalogCalls, 1);
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
