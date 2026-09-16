const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/out/' + (process.argv[2] || 'pipeline') + '.html');
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  console.log(JSON.stringify(await p.evaluate(() => {
    const w = document.getElementById('wrap');
    return { sh: w.scrollHeight, ch: w.clientHeight };
  })));
  await p.screenshot({ path: process.cwd() + '/out/' + (process.argv[2] || 'pipeline') + '.png' });
  await b.close();
})();
