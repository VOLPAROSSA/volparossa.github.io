import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
const {default:AxeBuilder}=await import('@axe-core/playwright');
import fs from 'node:fs';
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
const base=process.env.SITE_QA_URL || 'http://127.0.0.1:8000';
const output=process.env.SITE_QA_OUTPUT || 'work/qa';
fs.mkdirSync(output,{recursive:true});
const results=[];
function check(ok,message){if(!ok)throw Error(message)}
for(const width of [320,390,768,1440,1920]){
 const context=await browser.newContext({viewport:{width,height:900}});
 const page=await context.newPage();
 let errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
 for(const path of ['/','/docs/','/applications/','/contribute/','/privacy/','/accessibility/','/credits/','/examples/volparossa-application/']){
  await page.goto(base+path,{waitUntil:'networkidle'});
  await page.evaluate(async()=>{await document.fonts.ready;for(let y=0;y<document.body.scrollHeight;y+=700){scrollTo({top:y,behavior:'instant'});await new Promise(r=>setTimeout(r,100));}scrollTo({top:0,behavior:'instant'})});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Overflow ${path} ${width}`);
  check(await page.locator('h1').count()===1,`h1 ${path}`);
  check(await page.locator('img').evaluateAll(xs=>xs.filter(i=>i.getBoundingClientRect().width>0).every(i=>i.complete&&i.naturalWidth)),`Image ${path} ${width}`);
  check(errors.length===0,errors.join(','));
  if(width===390||width===1440){
   await page.addStyleTag({content:'.app-card,.shared,.milestones,.invitation{content-visibility:visible!important}'});
   const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
   results.push({width,path,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))});
  }
 }
 // Native mobile menu, enhanced Escape, visible focus and the skip link.
 if(width===390){
  await page.goto(base+'/',{waitUntil:'networkidle'});
  await page.keyboard.press('Tab');check(await page.locator('.skip-link').evaluate(e=>e===document.activeElement),'Skip link first');
  await page.keyboard.press('Enter');check(await page.locator('#main').evaluate(e=>e===document.activeElement),'Skip link targets main');
  await page.locator('.mobile-nav summary').click();check(await page.locator('.mobile-nav').evaluate(e=>e.open),'Menu opens');
  await page.keyboard.press('Escape');check(await page.locator('.mobile-nav').evaluate(e=>!e.open),'Escape closes');
  await page.locator('.mobile-nav summary').click();await page.locator('.mobile-nav a').filter({hasText:'Documentation'}).click();check(page.url().endsWith('/docs/'),'Mobile documentation destination');
  await page.goto(base+'/');await page.getByRole('link',{name:'Explore VOLPAROSSA',exact:false}).click();await page.waitForTimeout(1200);
  check(await page.locator('#shared-heading').evaluate(e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.top<innerHeight;}),'Shared-section anchor');
  // Emulate 200% text size without reducing CSS viewport.
  await page.goto(base+'/');await page.addStyleTag({content:'html{font-size:200%}'});
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'200% text overflow');
  await page.screenshot({path:output+'/text-zoom-200.png',fullPage:true});
 }
 await context.close();
}
const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
const page=await nojs.newPage();await page.goto(base+'/');await page.locator('.mobile-nav summary').click();await page.locator('.mobile-nav a').filter({hasText:'Documentation'}).click();check(page.url().endsWith('/docs/'),'No-JS menu');await page.goto(base+'/');check(await page.locator('.app-card').count()===3,'No-JS apps');
await nojs.close();
const reduced=await browser.newPage({reducedMotion:'reduce'});await reduced.goto(base+'/');check(await reduced.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior)==='auto','Reduced motion');await reduced.close();
fs.writeFileSync(output+'/browser-results.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results));
await browser.close();
check(results.every(r=>!r.violations.length),'Accessibility violations');
console.log('PASS: 40 responsive route checks; keyboard, native menu, no JavaScript, text resize and reduced motion.');
