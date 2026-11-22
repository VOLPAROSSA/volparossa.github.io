// Regression checks for uncropped artwork and shared screen geometry on large displays.
import {chromium, firefox, webkit} from 'playwright';
import fs from 'node:fs';
const base=process.env.SITE_QA_URL || 'http://127.0.0.1:8000';
const output=process.env.SITE_QA_OUTPUT || 'work/qa';
fs.mkdirSync(output,{recursive:true});
const results=[];
const assert=(ok,message)=>{if(!ok)throw Error(message)};
// Inspect the painted pixels, because WebKit can report correct SVG bounds
// even when a composited HTML layer is actually painted outside those bounds.
async function screenSamples(page) {
 const samples = [];
 for (const screen of await page.locator('.device-screens:visible image').all()) {
  const png = (await screen.screenshot()).toString('base64');
  samples.push(await screen.evaluate(async (el, capture) => {
   const channelSamples = async src => {
    const image = new Image();
    image.src = src;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = 12;
    canvas.height = 8;
    const context = canvas.getContext('2d');
    context.imageSmoothingQuality = 'high';
    // Avoid antialiasing at the bezel, and compare at a scale below the source resolution.
    const w = image.naturalWidth, h = image.naturalHeight;
    context.drawImage(image, w*.1, h*.1, w*.8, h*.8, 0, 0, 12, 8);
    return context.getImageData(0, 0, 12, 8).data;
   };
   const source = el.getAttribute('href');
   const expected = await channelSamples(source);
   const painted = await channelSamples('data:image/png;base64,' + capture);
   let error = 0;
   for (let i = 0; i < painted.length; i += 4) {
    for (let channel = 0; channel < 3; channel++) error += Math.abs(painted[i+channel] - expected[i+channel]);
   }
   const stage = el.ownerSVGElement, view = stage.viewBox.baseVal;
   const photo = stage.previousElementSibling.querySelector('img').getBoundingClientRect();
   const box = el.getBoundingClientRect();
   const expectedLeft = photo.left + (el.x.baseVal.value - view.x) * photo.width / view.width;
   const expectedTop = photo.top + (el.y.baseVal.value - view.y) * photo.height / view.height;
   const positionError = Math.max(Math.abs(box.left - expectedLeft), Math.abs(box.top - expectedTop));
   return {source, positionError, meanError: error / (12*8*3)};
  }, png));
 }
 return samples;
}
for(const [name,engine] of [['chromium',chromium],['firefox',firefox],['webkit',webkit]]){
 const browser=await engine.launch(name==='chromium'?{executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']}:{});
 for(const width of [320,390,768,1440,1920,2560,3840]){
  const page=await browser.newPage({viewport:{width,height:width>=2560?1440:900}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
  await page.goto(base+'/',{waitUntil:'networkidle'});
  await page.addStyleTag({content:'html{scroll-behavior:auto}.app-card,.shared,.milestones,.invitation{content-visibility:visible!important}'});
  await page.evaluate(async()=>{await document.fonts.ready;for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,150))}scrollTo(0,0)});
  // Let each lazy image enter the viewport and finish before leaving it.
  for(const img of await page.locator('img').all()){
   if(await img.isVisible()){
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(i=>i.decode());
   }
  }
  await page.evaluate(()=>scrollTo(0,0));
  const measurements=await page.evaluate(()=>{
   const hero=document.querySelector('.hero'),art=hero.querySelector('img'),rect=art.getBoundingClientRect();
   return {overflow:document.documentElement.scrollWidth>innerWidth,heroHeight:hero.getBoundingClientRect().height,imageHeight:rect.height,imageWidth:rect.width,
    marks:[...document.querySelectorAll('.upstream img')].map(i=>({loaded:i.complete&&i.naturalWidth>0,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),
    missing:[...document.images].filter(i=>i.getBoundingClientRect().width>0&&(!i.complete||!i.naturalWidth)).map(i=>i.src)};
  });
  assert(!measurements.overflow,`${name} ${width}: horizontal overflow`);
  assert(!measurements.missing.length,`${name} ${width}: missing images ${measurements.missing.join(", ")}`);
  if(width>800){
   assert(Math.abs(measurements.imageHeight-measurements.imageWidth*2/3)<1,`${name} ${width}: hero cropped`);
   assert(measurements.heroHeight>=measurements.imageHeight-1,`${name} ${width}: hero clipped by section`);
  }
  measurements.screens = await screenSamples(page);
  assert(measurements.screens.length===3&&measurements.screens.every(i=>i.positionError<1&&i.meanError<16),`${name} ${width}: screen paint mismatch ${JSON.stringify(measurements.screens)}`);
  assert(measurements.marks.length===3&&measurements.marks.every(i=>i.loaded&&i.width>20&&i.height>20),`${name} ${width}: missing upstream marks`);
  assert(!errors.length,errors.join('\n'));
  if([390,1440,2560].includes(width)){
   await page.screenshot({path:`${output}/${name}-${width}-page.png`,fullPage:true});
   await page.locator('.worktable').screenshot({path:`${output}/${name}-${width}-worktable.png`});
  }
  if(width===2560){
   for(const path of ['docs/','applications/']){
    await page.goto(base+'/'+path);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${name}: ${path} overflow`);
   }
   await page.goto(base+'/');await page.addStyleTag({content:'html{font-size:200%}'});
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`${name}: desktop 200% text overflow`);
  }
  results.push({browser:name,version:browser.version(),width,...measurements});await page.close();
 }
 // Projection and native navigation remain functional with scripting disabled.
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
 const page=await context.newPage();
 const responses = new Set();
 page.on('response', response => { if (response.ok()) responses.add(response.url()) });
 await page.goto(base+'/');
 await page.locator('.app-card.image').scrollIntoViewIfNeeded();
 const sources = await page.locator('.mobile-screens image').evaluateAll(images =>
  images.map(image => new URL(image.getAttribute('href'), document.baseURI).href));
 assert(sources.length===3&&sources.every(src=>responses.has(src)),`${name}: missing no-JS screenshots`);
 await page.locator('.mobile-nav summary').click();await page.getByRole('link',{name:'Documentation',exact:true}).first().click();assert(page.url().endsWith('/docs/'),`${name}: no-JS menu`);
 await context.close();await browser.close();
}
fs.writeFileSync(output+'/scene-results.json',JSON.stringify(results,null,2)+'\n');
console.log(`PASS: ${results.length} scene checks across Chromium, Firefox and WebKit, 320–3840 px; full hero, complete screens, original marks, text resize and no-JS navigation.`);
