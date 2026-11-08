import asyncio, sys, subprocess, os, shutil
from playwright.async_api import async_playwright
ratio=sys.argv[1]; out=sys.argv[2]; FPS=30
async def r():
  d=f'/tmp/frames_{ratio}'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    W,H=(1080,1350) if ratio=='4x5' else (1080,1920)
    pg=await b.new_page(viewport={'width':W,'height':H})
    await pg.goto(f'http://localhost:8765/hud-dev/video.html?capture&ratio={ratio}',wait_until='load')
    await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
    dur=await pg.evaluate('window.__duration')
    n=int(dur*FPS)
    for i in range(n):
      await pg.evaluate(f'window.__render({i/FPS})')
      await pg.screenshot(path=f'{d}/f{i:04d}.jpg', type='jpeg', quality=95)
    await b.close()
  subprocess.run(['ffmpeg','-v','error','-y','-framerate',str(FPS),'-i',f'{d}/f%04d.jpg','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',out],check=True)
  print(out, n, 'quadros')
asyncio.run(r())
