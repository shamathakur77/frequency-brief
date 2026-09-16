const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/out/card.html');
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  console.log(JSON.stringify(await p.evaluate(() => {
    const w = document.getElementById('wrap');
    const k = [...w.children].filter(e => !e.classList.contains('fx'));
    return { sh: w.scrollHeight, ch: w.clientHeight, last: Math.round(k[k.length-1].getBoundingClientRect().bottom) };
  })));
  await p.screenshot({ path: process.cwd() + '/out/card.png' });
  await b.close();
})();
