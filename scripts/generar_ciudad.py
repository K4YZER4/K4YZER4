"""Generate the animated contribution city. Python standard library only."""
from __future__ import annotations
import json
import random
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets' / 'code-city.svg'
API_URL = 'https://github-contributions-api.jogruber.de/v4/K4YZER4?y=last'
COLORS = {'background':'#101010','front':'#202020','side':'#131313','roof':'#303030','off_windows':'#3A3A3A','shadow':'#050505','accent_low':'#534C3D','accent_mid':'#897859','accent_high':'#BDA478','accent_max':'#EAD6AF'}
CELL_WEEK_X, CELL_WEEK_Y = 23, 4
CELL_DAY_X, CELL_DAY_Y = -23, 13
ORIGIN_X, ORIGIN_Y = 195, 160
MAX_HEIGHT, MAX_COUNT, MARGIN = 105, 12, 24
BUILD_SPREAD, BUILD_DURATION = 4.0, .65
LIGHT_MIN, LIGHT_MAX, FADE = .5, 4.0, .35
MONTHS = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']

def validate(raw):
    if not isinstance(raw,list) or not raw:
        raise RuntimeError('La respuesta no contiene contribuciones')
    days=[]
    for item in raw:
        if not isinstance(item,dict):
            raise RuntimeError('Día inválido')
        count,level=item.get('count'),item.get('level')
        if type(count) is not int or count<0 or type(level) is not int or not 0<=level<=4:
            raise RuntimeError('Cantidad o nivel inválidos')
        try:
            dt=date.fromisoformat(item['date'])
        except (ValueError,TypeError,KeyError) as e:
            raise RuntimeError('Fecha inválida') from e
        days.append({'date':dt,'count':count,'level':level})
    days.sort(key=lambda d:d['date'])
    for a,b in zip(days,days[1:]):
        if b['date']!=a['date']+timedelta(days=1):
            raise RuntimeError('Fechas duplicadas o días faltantes')
    return days

def fetch_contributions():
    req=urllib.request.Request(API_URL,headers={'User-Agent':'K4YZER4-code-city-generator/2.0'})
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            payload=json.load(response)
        return validate(payload.get('contributions') if isinstance(payload,dict) else None)
    except Exception as e:
        raise RuntimeError(f'No se pudieron consultar las contribuciones: {e}') from e

def polygon(points,fill,stroke=None):
    coords=' '.join(f'{x:.1f},{y:.1f}' for x,y in points)
    outline=f' stroke="{stroke}" stroke-width=".7"' if stroke else ''
    return f'<polygon points="{coords}" fill="{fill}"{outline}/>'

def light_animation(day,index):
    rng=random.Random('K4YZER4/'+day['date'].isoformat())
    holds=[rng.uniform(LIGHT_MIN,LIGHT_MAX) for _ in range(16)]
    total=sum(holds)+len(holds)*FADE
    frames=['0%{opacity:1}'];elapsed=0;value=1
    for hold in holds:
        elapsed+=hold
        frames.append(f'{elapsed/total*100:.5f}%{{opacity:{value}}}')
        elapsed+=FADE
        value=.12 if value==1 else 1
        frames.append(f'{min(elapsed/total*100,100):.5f}%{{opacity:{value}}}')
    delay=BUILD_SPREAD+BUILD_DURATION+rng.uniform(LIGHT_MIN,LIGHT_MAX)
    css=f'@keyframes light{index}{{'+''.join(frames)+'}'
    css+=f'.l{index}{{animation:light{index} {total:.5f}s linear {delay:.5f}s infinite;}}'
    return css

def generate(days):
    if not days:
        raise RuntimeError('No hay días')
    first,last=days[0]['date'],days[-1]['date']
    sunday=first-timedelta(days=(first.weekday()+1)%7)
    weeks=(last-sunday).days//7+1
    entries=[];bounds=[];styles=[]
    for index,d in enumerate(days):
        offset=(d['date']-sunday).days;week,weekday=divmod(offset,7)
        x=ORIGIN_X+week*CELL_WEEK_X+weekday*CELL_DAY_X
        y=ORIGIN_Y+week*CELL_WEEK_Y+weekday*CELL_DAY_Y
        count=d['count'];level=max(1,d['level'])
        h=12+round(MAX_HEIGHT*min(count,MAX_COUNT)/MAX_COUNT)
        fill=[COLORS['off_windows'],COLORS['accent_low'],COLORS['accent_mid'],COLORS['accent_high'],COLORS['accent_max']][level if count else 0]
        delay=index/max(1,len(days)-1)*BUILD_SPREAD
        label=escape(f"{d['date'].isoformat()}: {count} contribuciones")
        parts=[f'<g transform="translate({x} {y})" aria-label="{label}"><title>{label}</title>',polygon([(-3,2),(20,7),(34,-1),(10,-6)],COLORS['shadow']),f'<g class="grow" style="animation-delay:{delay:.5f}s">',polygon([(0,-h),(16,-h+4),(16,4),(0,0)],'#625746' if count else COLORS['front'],'#080808'),polygon([(16,-h+4),(25,-h-1),(25,-1),(16,4)],'#35312B' if count else COLORS['side'],'#080808'),polygon([(0,-h),(9,-h-5),(25,-h-1),(16,-h+4)],COLORS['accent_mid'] if count else COLORS['roof'],'#383838')]
        paths=[]
        for z in range(8,h-3,9):
            for col in range(2):
                wx=2.5+col*7;wy=-h+z+col*1.7
                paths.append(f'M{wx} {wy}l4 .9v4.2l-4 -.9z')
            paths.append(f'M18.5 {-h+z+1}l4 -2.1v4.2l-4 2.1z')
        if count:
            styles.append(light_animation(d,index))
            parts.append(f'<g class="lights l{index}">')
        parts.append(f'<path d="{" ".join(paths)}" fill="{fill}" opacity="{1 if count else .5}"/>')
        if count: parts.append('</g>')
        if count>MAX_COUNT//2:
            parts.append(f'<path d="M18 {-h-2}V{-h-13}" stroke="#D6C19A" stroke-width=".8"/><circle cx="18" cy="{-h-14}" r="1.3" fill="#EAD6AF"/>')
        parts.append('</g></g>')
        entries.append((weekday,week,''.join(parts)))
        bounds.append((x-4,y-h-(16 if count>6 else 5),x+35,y+8))
    minx=min(b[0] for b in bounds)-MARGIN;miny=min(b[1] for b in bounds)-MARGIN
    maxx=max(b[2] for b in bounds)+MARGIN;maxy=max(b[3] for b in bounds)
    axis=maxy+26;footer=axis+115;W=maxx-minx;H=footer-miny+MARGIN
    css='.grow{transform:scaleY(1);animation:build .65s ease-out both;transform-origin:0px 0px}.lights{opacity:1}@keyframes build{from{transform:scaleY(.015)}to{transform:scaleY(1)}}'+''.join(styles)+'@media(prefers-reduced-motion:reduce){.grow,.lights{animation:none!important;transform:none!important;opacity:1!important}}'
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.1f} {miny:.1f} {W:.1f} {H:.1f}" width="100%" role="img" aria-labelledby="city-title city-description">','<title id="city-title">Contribuciones en construcción</title>','<desc id="city-description">Actividad pública de K4YZER4. Un edificio por día. Altura limitada a 12 contribuciones. Primero se construye la ciudad; después las ventanas activas alternan suavemente. Las luces son decorativas.</desc>',f'<style>{css}</style>',f'<rect x="{minx}" y="{miny}" width="{W}" height="{H}" fill="#101010"/>']
    parts.extend(v for _,_,v in sorted(entries))
    parts.append(f'<g font-family="monospace"><path d="M{minx+14} {axis}H{maxx-14}" stroke="#534C3D"/>')
    seen=set();j=0
    for d in days:
        key=(d['date'].year,d['date'].month)
        if key in seen:continue
        seen.add(key)
        week=(d['date']-sunday).days//7
        x=ORIGIN_X+week*CELL_WEEK_X+6*CELL_DAY_X+8
        x=max(minx+28,min(maxx-28,x))
        row=axis+24+(j%2)*20
        label=MONTHS[d['date'].month-1]
        parts.append(f'<path d="M{x} {axis-5}v10" stroke="#897859"/><text x="{x}" y="{row}" text-anchor="middle" fill="#EAD6AF" font-size="14">{label}</text>')
        j+=1
    period=f"{first.strftime('%d/%m/%Y')} — {last.strftime('%d/%m/%Y')}"
    parts.extend([f'<text x="{minx+14}" y="{axis+75}" fill="#D6C19A" font-size="16">{period}</text>',f'<text x="{maxx-14}" y="{axis+75}" text-anchor="end" fill="#BDA478" font-size="12">Más reciente →</text>',f'<text x="{minx+14}" y="{axis+103}" fill="#999999" font-size="11">Un edificio por día · Luces decorativas · Altura limitada a {MAX_COUNT} contribuciones</text>','</g></svg>'])
    return '\n'.join(parts)+'\n'

def main():
    try:
        svg=generate(fetch_contributions())
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        temporary=OUTPUT.with_suffix('.svg.tmp')
        temporary.write_text(svg,encoding='utf-8',newline='\n')
        temporary.replace(OUTPUT)
    except Exception as e:
        print(f'Error: {e}',file=sys.stderr)
        return 1
    print(f'Generado {OUTPUT}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
