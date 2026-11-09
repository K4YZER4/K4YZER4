from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
import io
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
def ft(size,bold=False):
    candidates=[ROOT/'scripts'/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')]
    for p in candidates:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)
def gif(frames,durations,path):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
base=Image.new('RGB',(1200,310),'#eeeae2');d=ImageDraw.Draw(base)
d.text((26,78),'HORACIO',font=ft(112,True),fill='#171717');d.text((35,235),'ALVAREZ ESCOBEDO',font=ft(35),fill='#494640')
mask=Image.new('L',base.size);ImageDraw.Draw(mask).text((26,78),'HORACIO',font=ft(112,True),fill=255)
states=[]
for words in [['SOFTWARE','ENGINEERING'],['BACKEND','DEVELOPMENT'],['APIs','/','REAL-TIME','SYSTEMS']]:
    states.append(('',True,250))
    for k in range(1,len(words)+1): states.append((' '.join(words[:k]),True,500))
    for blink in range(6): states.append((' '.join(words),blink%2==0,220))
    for k in range(len(words)-1,-1,-1): states.append((' '.join(words[:k]),True,190))
frames=[];dur=[]
for j,(label,cursor,ms) in enumerate(states):
    im=base.copy();d=ImageDraw.Draw(im)
    d.text((35,26),label+(' _' if cursor else ''),font=ft(16),fill='#444444')
    d.text((1060,20),['[ / ]','[ > ]','[ _ ]'][(j//3)%3],font=ft(24),fill='#66615b')
    d.line((35,286,1165,286),fill='#d3cfc7');length=1130*min(1,j/8)
    d.line((35,286,35+length,286),fill='#171717',width=2)
    if j<9: d.ellipse((32+length,283,38+length,289),fill='#494640')
    if 6<=j<22:
        x=int(-150+(j-6)*1400/15);band=Image.new('L',base.size);bd=ImageDraw.Draw(band)
        for offset in range(-75,76): bd.line((x+offset,0,x+offset,310),fill=round(90*(1-abs(offset)/76)))
        im=Image.composite(Image.new('RGB',base.size,'#77736d'),im,ImageChops.multiply(mask,band))
    frames.append(im.convert('P',palette=Image.Palette.ADAPTIVE,colors=64));dur.append(ms)
gif(frames,dur,OUT/'cabecera.gif');frames[5].save(OUT/'cabecera-estatica.png')
phrases=['APIs REST / WEBSOCKETS','NESTJS / NODE.JS','DATOS → REGLAS DE NEGOCIO','BUILD → TEST → DEPLOY','AWS / RENDER / VERCEL','AUTH → ROLES → PERMISSIONS']
frames=[]
for s in phrases:
    for j in range(20):
        im=Image.new('RGB',(1000,120),'#171717');d=ImageDraw.Draw(im)
        n=min(len(s),round((j+1)*len(s)/11))
        d.text((28,39),'> '+s[:n]+(' _' if j%6<3 else ''),font=ft(27,True),fill='#eeeae2')
        frames.append(im.convert('P',palette=Image.Palette.ADAPTIVE,colors=32))
gif(frames,100,OUT/'terminal.gif');frames[19].save(OUT/'terminal-estatica.png')
im=Image.new('RGB',(360,470),'#e7e3db');d=ImageDraw.Draw(im)
d.ellipse((120,90,240,210),outline='#77736d',width=3);d.arc((65,195,295,415),180,360,fill='#77736d',width=3)
d.text((76,422),'TU FOTO AQUÍ',font=ft(25),fill='#494640');im.save(OUT/'foto.png')
for folder,title,subtitle in [('restaurant-management','RESTAURANT','MANAGEMENT SAAS / EN DESARROLLO'),('fitness-platform','FITNESS','PLATFORM / EN DESARROLLO'),('_plantilla','PROJECT','CASE STUDY / COMPLETAR')]:
    dest=ROOT/'proyectos'/folder/'assets';dest.mkdir(parents=True,exist_ok=True)
    im=Image.new('RGB',(1200,310),'#eeeae2');d=ImageDraw.Draw(im)
    d.text((35,26),subtitle,font=ft(16),fill='#444444');d.text((26,78),title,font=ft(112 if len(title)<10 else 88,True),fill='#171717')
    d.text((35,235),'BACKEND / PROJECT NOTES',font=ft(35),fill='#494640');d.line((35,286,1165,286),fill='#171717',width=2);im.save(dest/'portada.png')
    im=Image.new('RGB',(700,500),'#e7e3db');d=ImageDraw.Draw(im)
    d.text((26,30),'EVIDENCIA VISUAL',font=ft(18),fill='#494640');d.text((26,160),'Tu captura o\ndiagrama aquí.',font=ft(42,True),fill='#242321')
    d.text((26,360),'Marcador; no es una captura del producto.',font=ft(19),fill='#66615c');im.save(dest/'captura.png')
