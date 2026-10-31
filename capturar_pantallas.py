import threading,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from app import server
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
srv=make_server('127.0.0.1',8050,server,threaded=True)
threading.Thread(target=srv.serve_forever,daemon=True).start()
p=Path(__file__).resolve().parent/'capturas';p.mkdir(exist_ok=True)
with sync_playwright() as w:
 b=w.chromium.launch(headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 page.goto('http://127.0.0.1:8050',wait_until='networkidle')
 page.wait_for_function("document.querySelectorAll('.js-plotly-plot').length===6")
 page.screenshot(path=str(p/'tablero.png'),full_page=True)
 for n,id in enumerate(['mapa','mes','violencia','menor','sexo_dep','edad']):page.locator('#'+id).screenshot(path=str(p/(id+'.png')))
 page.locator('#causas').screenshot(path=str(p/'causas.png'))
 b.close()
srv.shutdown()
print('Capturas obtenidas')
