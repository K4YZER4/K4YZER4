"""Contribution city with diagonal month labels and sequential SVG animations."""
import json
import random
import sys
import urllib.request
from datetime import date,timedelta
from pathlib import Path
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'assets'/'code-city.svg'
API_URL='https://github-contributions-api.jogruber.de/v4/K4YZER4?y=last'
MONTHS=['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
PALETTE=['#3A3A3A','#534C3D','#897859','#BDA478','#EAD6AF']
LIGHT_MIN,LIGHT_MAX,FADE=.5,4.0,.35
MAX_COUNT,MAX_HEIGHT=12,105

def validate(raw):
    if not isinstance(raw,list) or not raw:raise RuntimeError('No hay contribuciones')
    result=[]
    for d in raw:
        if not isinstance(d,dict) or type(d.get('count')) is not int or d['count']<0 or type(d.get('level')) is not int or not 0<=d['level']<=4:raise RuntimeError('Datos inválidos')
        result.append({'date':date.fromisoformat(d['date']),'count':d['count'],'level':d['level']})
    result.sort(key=lambda d:d['date'])
    for a,b in zip(result,result[1:]):
        if b['date']!=a['date']+timedelta(days=1):raise RuntimeError('Fechas faltantes o duplicadas')
    return result

def fetch_contributions():
    req=urllib.request.Request(API_URL,headers={'User-Agent':'K4YZER4-code-city/2.1'})
    with urllib.request.urlopen(req,timeout=30) as response:payload=json.load(response)
    return validate(payload.get('contributions') if isinstance(payload,dict) else None)

def poly(points,fill,stroke='#080808'):
    return '<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width=".7"/>'

def lighting(d,i,floor):
    rng=random.Random('K4YZER4/'+d['date'].isoformat()+'/floor/'+str(floor))
    holds=[rng.uniform(LIGHT_MIN,LIGHT_MAX) for _ in range(16)]
    total=sum(holds)+16*FADE;elapsed=0;value=1;frames=['0%{opacity:1}']
    for hold in holds:
        elapsed+=hold;frames.append(f'{elapsed/total*100:.5f}%{{opacity:{value}}}')
        elapsed+=FADE;value=.12 if value==1 else 1
        frames.append(f'{min(100,elapsed/total*100):.5f}%{{opacity:{value}}}')
    return f'@keyframes light{i}_{floor}{{'+''.join(frames)+'}'+f'.l{i}_{floor}{{animation:light{i}_{floor} {total:.5f}s linear {4.65+rng.uniform(.5,4):.5f}s infinite}}'

def generate(days):
    if not days:raise RuntimeError('No hay datos')
    first,last=days[0]['date'],days[-1]['date'];sunday=first-timedelta(days=(first.weekday()+1)%7)
    weeks=(last-sunday).days//7+1
    # Match the dated HTML: shallow chronological slope and labels along the front edge.
    W=weeks*24+270;H=560
    entries=[];css=[]
    for i,d in enumerate(days):
        week,weekday=divmod((d['date']-sunday).days,7)
        x=210+week*24-weekday*22;y=160+week*2.1+weekday*14
        count=d['count'];h=12+round(MAX_HEIGHT*min(count,MAX_COUNT)/MAX_COUNT)
        c=PALETTE[max(1,d['level']) if count else 0]
        label=escape(f"{d['date'].isoformat()}: {count} contribuciones")
        p=[f'<g transform="translate({x:.1f} {y:.1f})" aria-label="{label}"><title>{label}</title>',poly([(-3,2),(20,7),(34,-1),(10,-6)],'#050505'),f'<g class="grow" style="animation-delay:{i/max(1,len(days)-1)*4:.5f}s">',poly([(0,-h),(16,-h+4),(16,4),(0,0)],'#625746' if count else '#202020'),poly([(16,-h+4),(25,-h-1),(25,-1),(16,4)],'#35312B' if count else '#131313'),poly([(0,-h),(9,-h-5),(25,-h-1),(16,-h+4)],'#897859' if count else '#303030','#383838')]
        for floor,z in enumerate(range(8,h-3,9)):
            paths=[]
            for col in range(2):
                wx=2.5+col*7;wy=-h+z+col*1.7
                paths.append(f'M{wx} {wy}l4 .9v4.2l-4 -.9z')
            paths.append(f'M18.5 {-h+z+1}l4 -2.1v4.2l-4 2.1z')
            if count:
                css.append(lighting(d,i,floor))
                p.append(f'<g class="lights l{i}_{floor}" data-floor="{floor}">')
            p.append(f'<path d="{" ".join(paths)}" fill="{c}" opacity="{1 if count else .5}"/>')
            if count:
                p.append('</g>')
        if count>6:p.append(f'<path d="M18 {-h-2}V{-h-13}" stroke="#D6C19A" stroke-width=".8"/><circle cx="18" cy="{-h-14}" r="1.3" fill="#EAD6AF"/>')
        p.append('</g></g>');entries.append((weekday,week,''.join(p)))
    style='.grow{transform:scaleY(1);transform-origin:0px 0px;animation:build .65s ease-out both}.lights{opacity:1}@keyframes build{from{transform:scaleY(.015)}to{transform:scaleY(1)}}'+''.join(css)+'@media(prefers-reduced-motion:reduce){.grow,.lights{animation:none!important;transform:none!important;opacity:1!important}}'
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="city-title city-description">','<title id="city-title">Contribuciones en construcción</title>','<desc id="city-description">Ciudad de contribuciones públicas de K4YZER4. Un edificio por día; altura limitada visualmente a 12 contribuciones. Meses junto a la base y rango de fechas al pie. Luces decorativas después de la construcción.</desc>',f'<style>{style}</style>',f'<rect width="{W}" height="{H}" fill="#101010"/>']
    parts.extend(s for _,_,s in sorted(entries));parts.append('<g font-family="monospace">')
    seen=set()
    for d in days:
        key=(d['date'].year,d['date'].month)
        if key in seen:continue
        seen.add(key);week=(d['date']-sunday).days//7
        x=210+week*24-6*22+8;y=160+week*2.1+6*14+20
        parts.append(f'<path d="M{x:.1f} {y:.1f}v13" stroke="#897859"/><text x="{x:.1f}" y="{y+32:.1f}" text-anchor="middle" fill="#D6C19A" font-size="12">{MONTHS[d["date"].month-1]}</text>')
        if len(seen)==1 or d['date'].month==1:parts.append(f'<text x="{x:.1f}" y="{y+48:.1f}" text-anchor="middle" fill="#897859" font-size="10">{d["date"].year}</text>')
    parts.extend([f'<line x1="64" y1="430" x2="{W-65}" y2="430" stroke="#534C3D"/>',f'<path d="M{W-72} 426l7 4-7 4" fill="none" stroke="#BDA478"/>','<text x="64" y="417" fill="#897859" font-size="11">MÁS ANTIGUO</text>',f'<text x="{W-64}" y="417" text-anchor="end" fill="#BDA478" font-size="11">MÁS RECIENTE</text>',f'<text x="64" y="457" fill="#D6C19A" font-size="14">{first.strftime("%d/%m/%Y")} — {last.strftime("%d/%m/%Y")}</text>','<text x="64" y="483" fill="#8D9189" font-size="10">Cada edificio representa un día · Altura limitada a 12 contribuciones</text>'])
    lx=W-245
    parts.append(f'<text x="{lx}" y="452" fill="#999999" font-size="10">Menos</text>')
    for i,c in enumerate(['#242424']+PALETTE[1:]):parts.append(f'<rect x="{lx+42+i*19}" y="442" width="14" height="14" rx="2" fill="{c}" stroke="#555555" stroke-width=".5"/>')
    parts.extend([f'<text x="{lx+145}" y="452" fill="#999999" font-size="10">Más</text>','</g></svg>'])
    return '\n'.join(parts)+'\n'

def main():
    try:
        result=generate(fetch_contributions());OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        temporary=OUTPUT.with_suffix('.svg.tmp');temporary.write_text(result,encoding='utf-8',newline='\n');temporary.replace(OUTPUT)
    except Exception as e:
        print(f'Error: {e}',file=sys.stderr);return 1
    print(f'Generado {OUTPUT}');return 0
if __name__=='__main__':raise SystemExit(main())
