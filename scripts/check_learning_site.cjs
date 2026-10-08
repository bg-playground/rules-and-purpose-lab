// Browser verification for the generated learning pages, with screenshots for review.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE);
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 fs.mkdirSync('site-review',{recursive:true});
 try {
  for(const [name,width,height,scheme] of [['desktop',1440,1000,'light'],['phone',390,844,'light'],['phone-dark',390,844,'dark'],['tablet',768,1024,'dark']]){
   const page=await browser.newPage({viewport:{width,height},colorScheme:scheme});
   for(const route of ['index.html','slides.html','workshop.html']){
    const response=await page.goto('http://127.0.0.1:8765/'+route);
    if(response.status()!==200)throw Error('Failed route '+route);
    const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,h1:document.querySelectorAll('h1').length,slides:document.querySelectorAll('.slide').length}));
    if(metrics.overflow||metrics.h1!==1)throw Error(name+' '+route+' layout '+JSON.stringify(metrics));
    if(route==='slides.html'){
     if(metrics.slides!==7)throw Error('Expected seven slides');
     await page.getByRole('link',{name:'Slide 4',exact:true}).click();
     if(!page.url().endsWith('#slide-4'))throw Error('Slide fragment failed');
     await page.screenshot({path:'site-review/'+name+'-slide-4.png'});
    }else await page.screenshot({path:'site-review/'+name+'-'+route+'.png',fullPage:true});
   }
   await page.goto('http://127.0.0.1:8765/slides.html');
   for(const ext of ['pdf','pptx']){
    const r=await page.request.get('http://127.0.0.1:8765/downloads/Rules_and_Purpose_Lab_Teaching_Deck.'+ext);
    const body=await r.body();
    if(!r.ok()||!body.subarray(0,4).equals(Buffer.from(ext==='pdf'?'%PDF':'PK\x03\x04','binary')))throw Error('Bad '+ext+' download');
   }
   await page.close();
   console.log(name+': pages, width, headings, slide navigation, and downloads pass');
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
