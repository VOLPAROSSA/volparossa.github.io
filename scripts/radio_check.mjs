// Exercise the hidden radio without depending on Spotify availability.
import assert from 'node:assert/strict';
import {chromium, firefox, webkit} from 'playwright';

const site = process.env.SITE_QA_URL || 'http://127.0.0.1:8000';
const playlist = 'https://open.spotify.com/embed/playlist/6ricSn5ycy3agLA5SmL5dM';
const services = [
  'link.deezer.com', 'music.youtube.com', 'open.qobuz.com', 'tidal.com',
  'music.amazon.com', 'listenbrainz.org', 'soundcloud.com', 'open.spotify.com'
];

for (const engine of [chromium, firefox, webkit]) {
  const browser = await engine.launch(engine === chromium ? {
    executablePath: process.env.CHROME_PATH, args: ['--no-sandbox']
  } : {});
  try {
    for (const width of [320, 390, 820, 1440, 2560, 3840]) {
      const touch = width <= 390;
      const reduce = width === 320 || width === 820;
      const page = await browser.newPage({
        viewport: {width, height: touch ? 844 : 900},
        hasTouch: touch, reducedMotion: reduce ? 'reduce' : 'no-preference'
      });
      const external = [];
      page.on('request', req => {
        if (new URL(req.url()).origin !== new URL(site).origin) external.push(req.url());
      });
      await page.route(playlist + '**', route => route.fulfill({contentType: 'text/html', body: '<title>Playlist</title>'}));
      await page.goto(site);
      const button = page.getByRole('button', {name: 'VOLPAROSSA Radio', exact: true});
      const section = page.locator('#volparossa-radio');
      await page.evaluate(() => scrollTo({top: document.documentElement.scrollHeight, behavior: 'instant'}));
      await page.waitForFunction(() => document.querySelector('.shelf-edit').naturalWidth > 0);
      await button.scrollIntoViewIfNeeded();
      assert(await section.isHidden());
      assert.equal(await page.locator('iframe').count(), 0);
      assert.deepEqual(external, []);

      // The whole cabinet, including its meters, must fit inside the visible scene.
      assert(await button.evaluate(b => {
        const r = b.getBoundingClientRect();
        const w = b.closest('.chapter-window').getBoundingClientRect();
        return r.width >= 44 && r.height >= 44 && r.left >= w.left - 1 && r.right <= w.right + 1
          && r.top >= w.top - 1 && r.bottom <= w.bottom + 1
          && b.contains(document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2));
      }), 'Cabinet clipped or unclickable at ' + width);

      if (!touch) {
        await button.hover();
        await page.waitForFunction(() => getComputedStyle(document.querySelector('.meter-light')).opacity === '1');
        const motion = await button.locator('.meter-needle').evaluateAll(paths => paths.map(p => getComputedStyle(p).animationName));
        assert.deepEqual(motion, Array(2).fill(reduce ? 'none' : 'meter-swing'));
        await page.mouse.move(0, 0);
        await button.focus();
        await page.keyboard.press('Enter');
      } else {
        await button.tap();
      }
      await page.waitForFunction(() => document.activeElement.id === 'radio-heading');
      assert.equal(await button.getAttribute('aria-expanded'), 'true');
      await section.waitFor({state: 'visible'});
      const frame = section.locator('iframe');
      assert((await frame.getAttribute('src')).startsWith(playlist + '?'));
      await frame.contentFrame().locator('title').waitFor({state:'attached'});
      assert.equal(external.length, 1);
      assert.deepEqual(await section.locator('.radio-stations a').evaluateAll(links => links.map(a => a.hostname)), services);
      await page.waitForFunction(() => [...document.querySelectorAll('.radio-stations img')].every(i => i.naturalWidth > 0));
      const tiles = await section.locator('.radio-stations img').evaluateAll(images =>
        images.map(image => [image.offsetWidth, image.offsetHeight]));
      assert(tiles.every(([w, h]) => w >= 44 && w === h && w === tiles[0][0]), 'Platform tiles must be equally sized squares');
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      if (touch) await section.getByRole('button', {name:'Close VOLPAROSSA Radio'}).tap();
      else await page.keyboard.press('Escape');
      assert(await section.isHidden());
      assert.equal(await section.locator('iframe').count(), 0);
      assert.equal(await button.getAttribute('aria-expanded'), 'false');
      assert(await button.evaluate(b => b === document.activeElement));
      await button.press('Space');
      assert.equal(await section.locator('iframe').count(), 1);
      await button.click();
      assert(await section.isHidden());
      await page.close();
    }
    console.log(engine.name(), browser.version(), 'radio passed at six widths');
  } finally {
    await browser.close();
  }
}
