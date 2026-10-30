// Regression checks for uncropped artwork and shared screen geometry on large displays.
import {chromium, firefox} from 'playwright';
import fs from 'node:fs';
const base=process.env.SITE_QA_URL || 'http://127.0.0.1:8000';
const output=process.env.SITE_QA_OUTPUT || 'work/qa';
fs.mkdirSync(output,{recursive:true});
const results=[];
const assert=(ok,message)=>{if(!ok)throw Error(message)};
for(const [name,engine] of [['chromium',chromium],['firefox',firefox]]){
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
    screens:[...document.querySelectorAll('.screen')].filter(i=>i.getBoundingClientRect().width>0).map(i=>({loaded:i.complete&&i.naturalWidth>0,fit:getComputedStyle(i).objectFit})),
    marks:[...document.querySelectorAll('.upstream img')].map(i=>({loaded:i.complete&&i.naturalWidth>0,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),
    missing:[...document.images].filter(i=>i.getBoundingClientRect().width>0&&(!i.complete||!i.naturalWidth)).map(i=>i.src)};
  });
  assert(!measurements.overflow,`${name} ${width}: horizontal overflow`);
  assert(!measurements.missing.length,`${name} ${width}: missing images ${measurements.missing.join(", ")}`);
  if(width>800){
   assert(Math.abs(measurements.imageHeight-measurements.imageWidth*2/3)<1,`${name} ${width}: hero cropped`);
   assert(measurements.heroHeight>=measurements.imageHeight-1,`${name} ${width}: hero clipped by section`);
  }
  assert(measurements.screens.length===3&&measurements.screens.every(i=>i.loaded&&i.fit==='contain'),`${name} ${width}: incomplete device screenshots`);
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
 const page=await context.newPage();await page.goto(base+'/');await page.locator('.app-card.image').scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>[...document.querySelectorAll('.mobile-screens .screen')].every(i=>i.complete&&i.naturalWidth));
 await page.locator('.mobile-nav summary').click();await page.getByRole('link',{name:'Documentation',exact:true}).first().click();assert(page.url().endsWith('/docs/'),`${name}: no-JS menu`);
 await context.close();await browser.close();
}
fs.writeFileSync(output+'/scene-results.json',JSON.stringify(results,null,2)+'\n');
console.log(`PASS: ${results.length} scene checks across Chromium and Firefox, 320–3840 px; full hero, complete screens, original marks, text resize and no-JS navigation.`);
