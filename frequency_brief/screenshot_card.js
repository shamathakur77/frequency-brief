// Render out/card.html to out/card.png at exactly 1080x1350.
// Layout is asserted, not eyeballed: any overflow fails the build.
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const out = path.join(process.cwd(), 'out');
  const browser = await chromium.launch(
    process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });

  await page.goto('file://' + path.join(out, 'card.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  const m = await page.evaluate(() => {
    const w = document.getElementById('wrap');
    const kids = [...w.children];
    const last = kids[kids.length - 1].getBoundingClientRect();
    return { scrollHeight: w.scrollHeight, clientHeight: w.clientHeight,
             lastBottom: Math.round(last.bottom) };
  });

  if (m.scrollHeight !== m.clientHeight) {
    await browser.close();
    console.error(`overflow: content ${m.scrollHeight}px in a ${m.clientHeight}px card`);
    process.exit(1);
  }

  await page.screenshot({ path: path.join(out, 'card.png') });
  await browser.close();
  console.log(`wrote out/card.png, last element bottom ${m.lastBottom}`);
})();
