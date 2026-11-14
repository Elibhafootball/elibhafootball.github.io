(()=>{'use strict';
const colors={"Adelaide Wanderers":"#c92c32","AFC Droy":"#33383f","Antonito Boilermen":"#db721f","Baptist Railway Athletic":"#25824b","Beaumaris United":"#626b76","Birkstall Welfare":"#273d68","Boulton Rovers":"#17623b","Brath Vale":"#2669b5","Brenton Mill Spartans":"#2669b5","Bricknell Town":"#33383f","Brighthaven Regent":"#2669b5","Brizes Apps":"#bb8c10","Brunigton Town":"#273d68","Camptown Athletic":"#db721f","Carlton Town":"#c92c32","Carmichael Town":"#25824b","Chapeltown Academical":"#428cb9","Clawton-in-Ribbert":"#c92c32","Clevedon Magna":"#17623b","Clifton Albion":"#bb8c10","Copeside Union":"#33383f","Courteney Villa":"#80394d","Courton Lees":"#80394d","Crayness United":"#2669b5","Deportivo Leon":"#33383f","Dockside Admirals":"#bb8c10","Draycott Town":"#2669b5","Durham West End":"#c92c32","Dynamo Denton":"#2669b5","East Camberwell United":"#c92c32","Edwalton":"#25824b","Eleanor's Bay Cosmos":"#274b86","FC Brados":"#741d38","Frotes Juniors":"#33383f","Georgetown Atlantic":"#273d68","Gresdon Methodists":"#c92c32","Gresdon Town":"#db721f","Hardwick Rovers":"#c92c32","Hassockstown Ramblers":"#33383f","Heckingborough":"#2669b5","Hereford & Aspley":"#db721f","Holloway Sands":"#c92c32","Hoxbeth Amateurs":"#80394d","Jessopstown Rangers":"#33383f","Jostinians":"#c92c32","Kingsport Bohemians":"#33383f","Kintyre Coastguard":"#bf8219","Kirkby Harriers":"#2669b5","La Robla":"#c92c32","Lambeth":"#c92c32","Lansdowne 1981":"#c92c32","Large United":"#c92c32","Large Victoria":"#274b86","Lavender Park":"#428cb9","Lennox Meridian":"#c92c32","Little Antonito":"#428cb9","Little Padstow":"#33383f","Mannion":"#80394d","Maulover Bay Rowdies":"#626b76","New Lincoln":"#c92c32","New Lincoln University":"#274b86","New Plymouth Mariners":"#25824b","Newark Port":"#33383f","North Denton United":"#428cb9","Palmerston United":"#274b86","Partizan Warfield":"#33383f","Petherick Ferry":"#273d68","Port Bristol Rovers":"#2669b5","Port Fowey Royals":"#c92c32","Port Orient Battery":"#9e3336","Princes Yeomouth":"#273d68","Purditon Town":"#c92c32","Queenstown Riot":"#2669b5","Racing Club":"#428cb9","Real San Domingo":"#33383f","Redmond Town":"#c92c32","Rocastle United":"#c92c32","Sancti Spiritus":"#bb8c10","Santiago de Brados":"#c92c32","Serjeant's Bay":"#25824b","South Bay Sports":"#db721f","Southcastle United":"#33383f","St John Meridian":"#bb8c10","St Jude":"#c92c32","St Luke's Yonder":"#c92c32","St Vincent All Stars":"#2669b5","Stoke Town":"#c92c32","Stoneleigh Town":"#697582","Stoughborough Town":"#25824b","Sunnymede Rangers":"#bb8c10","Swannbridge Town":"#c92c32","Syrell Regis Rescue":"#db721f","The Maldons":"#274b86","The Mavericks":"#c92c32","Thorpe St Martin":"#274b86","Torpedo Webbstown":"#33383f","Uffington Edge":"#274b86","Vaughanstown":"#bb8c10","Walker Celtic":"#25824b","Walpool International":"#33383f","Walpool Seagulls":"#2669b5","Warfield Industrial":"#c92c32","West Heath Rangers":"#697582","West Walpool Juniors":"#bb8c10","Westville Wanderers":"#c92c32","Whatton 004":"#2669b5","Whitburn Carew":"#c92c32","Wincanton Athletic":"#c92c32","Windaybank Thistle":"#bb8c10","Worthington Rovers":"#c92c32","Wyvernmouth Dockers":"#c92c32"};
const root=document.querySelector('main');if(!root)return;
const blocks=[...root.querySelectorAll('.round-block')];const rounds=blocks.map(b=>{const rows=[...b.querySelectorAll('.live-table tbody tr')];return rows.map((row,i)=>{const a=row.querySelector('.live-team a');return a?{name:a.textContent.trim(),href:a.getAttribute('href'),pos:parseInt(row.cells[0]?.textContent,10),played:parseInt(row.cells[1]?.textContent,10),pts:row.querySelector('.live-pts')?.textContent.trim()}:null}).filter(Boolean)}).filter(x=>x.length>0);
if(rounds.length<2)return;
// Associate each recorded result with the club's next game number, not the round label.
const resultsByClub=new Map();
for(const block of blocks){
  for(const tr of block.querySelectorAll('table.results tbody tr')){
    const cells=tr.querySelectorAll('td');
    if(cells.length<3)continue;
    const home=cells[0].textContent.trim(),score=cells[1].textContent.trim(),away=cells[2].textContent.trim();
    if(!/^\\d+\\s*[–—-]\\s*\\d+$/.test(score))continue;
    const result=home+' '+score.replace(/\\s+/g,'')+' '+away;
    for(const club of [home,away]){
      if(!resultsByClub.has(club))resultsByClub.set(club,[]);
      resultsByClub.get(club).push(result);
    }
  }
}
const final=rounds[rounds.length-1];const n=final.length;
const teams=final.map(r=>{const byGame=new Map();for(const round of rounds){const row=round.find(x=>x.name===r.name);if(row&&Number.isInteger(row.played)&&row.played>0&&!byGame.has(row.played))byGame.set(row.played,row)}
const maxPlayed=Math.max(...final.map(x=>x.played||0));const positions=Array.from({length:maxPlayed},(_,i)=>byGame.get(i+1)?.pos??null);
const points=Array.from({length:maxPlayed},(_,i)=>byGame.get(i+1)?.pts??'');
const results=Array.from({length:maxPlayed},(_,i)=>resultsByClub.get(r.name)?.[i]??null);
const slug=r.href.split('/').pop().replace('.html','.png');return {name:r.name,href:r.href,crest:'../clubs/crests/'+slug,colors:[colors[r.name]||'#64748b'],positions,points,results};});
const matchCount=Math.max(...teams.map(t=>t.positions.length));
const section=document.createElement('section');section.className='position-chart-section';section.innerHTML='<h2>League position by games played</h2><p class="position-chart-help">Positions after each club’s 1st, 2nd, 3rd game, etc. Hover over or select a club to follow its season. Click again to show all clubs.</p><div class="position-chart-scroll"><div class="position-chart-inner"><svg class="position-chart-svg" role="img" aria-label="League positions after each club’s games played"></svg><div class="position-chart-tooltip" hidden></div></div></div>';
const anchor=root.querySelector('.round-block');if(anchor)anchor.before(section);else root.append(section);
const svg=section.querySelector('svg'),tip=section.querySelector('.position-chart-tooltip');const NS='http://www.w3.org/2000/svg';const W=1100,H=Math.max(620,n*34+55),left=43,right=855,top=26,bottom=H-34,lab=right+23;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.style.height=H+'px';
const el=(tag,attrs,parent=svg)=>{const e=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,String(v));parent.append(e);return e};
const X=i=>left+i*(right-left)/(matchCount-1),Y=p=>top+(p-1)*(bottom-top)/(n-1);
for(let p=1;p<=n;p++){el('line',{x1:left,x2:right,y1:Y(p),y2:Y(p),stroke:'#8b96a4','stroke-opacity':'.19'});const t=el('text',{x:left-12,y:Y(p)+4,'text-anchor':'end',fill:'#7a8491','font-size':12});t.textContent=p}
for(let i=0;i<matchCount;i++){if(i%Math.max(1,Math.ceil(matchCount/12))!==0&&i!==matchCount-1)continue;const t=el('text',{x:X(i),y:H-8,'text-anchor':'middle',fill:'#7a8491','font-size':12});t.textContent=i+1}
let selected=null,hovered=null;const groups=[];
teams.forEach((team,index)=>{const group=el('g',{'data-team':team.name});const points=team.positions.map((p,i)=>p==null?null:[X(i),Y(p)]).filter(Boolean);const d=points.map((p,i)=>(i?'L':'M')+p.join(',')).join(' ');const line=el('path',{d,fill:'none',stroke:team.colors[0],'stroke-width':2.2,'stroke-linejoin':'round','stroke-linecap':'round'},group);
let secondary=null;if(team.colors[1])secondary=el('path',{d,fill:'none',stroke:team.colors[1],'stroke-width':2.2,'stroke-dasharray':'7 7','stroke-linejoin':'round','stroke-linecap':'round'},group);
const hit=el('path',{d,fill:'none',stroke:'transparent','stroke-width':13,style:'cursor:pointer'},group);
const finalY=Y(index+1);const connector=el('line',{x1:right,x2:lab-7,y1:finalY,y2:finalY,stroke:team.colors[0],'stroke-width':2},group);
const label=el('g',{role:'button',tabindex:0,'aria-label':'Highlight '+team.name,style:'cursor:pointer'},group);
el('rect',{x:lab-5,y:finalY-15,width:W-lab+5,height:30,fill:'transparent'},label);
const crest=el('image',{x:lab,y:finalY-11,width:22,height:22,href:team.crest},label);
const name=el('text',{x:lab+30,y:finalY+5,'font-size':14,fill:'currentColor'},label);name.textContent=team.name;
const select=()=>{selected=selected===team.name?null:team.name;render()};label.addEventListener('click',select);hit.addEventListener('click',select);label.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();select()}});[label,hit].forEach(node=>{node.addEventListener('mouseenter',()=>{hovered=team.name;render()});node.addEventListener('mouseleave',()=>{hovered=null;render()})});
hit.addEventListener('mousemove',e=>{const rect=svg.getBoundingClientRect();const px=(e.clientX-rect.left)*W/rect.width;const idx=Math.max(0,Math.min(matchCount-1,Math.round((px-left)/(right-left)*(matchCount-1))));const position=team.positions[idx];
if(position==null){tip.hidden=true;return}
tip.hidden=false;
tip.textContent=(team.results[idx]||team.name+' · Game '+(idx+1))+', '+position+ordinal(position)+', '+team.points[idx]+'pts';
const inner=section.querySelector('.position-chart-inner');
const innerRect=inner.getBoundingClientRect();
const scaleX=rect.width/W,scaleY=rect.height/H;
const pointX=rect.left-innerRect.left+X(idx)*scaleX;
const pointY=rect.top-innerRect.top+Y(position)*scaleY;
const tooltipWidth=tip.offsetWidth;
const tooltipHeight=tip.offsetHeight;
tip.style.left=Math.max(4,Math.min(inner.clientWidth-tooltipWidth-4,pointX-tooltipWidth/2))+'px';
tip.style.top=Math.max(3,pointY-tooltipHeight-12)+'px'});hit.addEventListener('mouseleave',()=>tip.hidden=true);
groups.push({team,group,line,secondary,connector,label,name})});
function ordinal(n){return n%100>=11&&n%100<=13?'th':n%10===1?'st':n%10===2?'nd':n%10===3?'rd':'th'}
function render(){const active=hovered||selected;for(const g of groups){const on=g.team.name===active;const faded=active&&!on;g.line.style.opacity=faded?'.11':active?'1':'.36';if(g.secondary)g.secondary.style.opacity=faded?'.11':active?'1':'.55';g.line.setAttribute('stroke-width',on?4:2.2);if(g.secondary)g.secondary.setAttribute('stroke-width',on?4:2.2);g.connector.style.opacity=faded?'.2':'1';g.name.style.opacity=faded?'.48':'1';g.name.style.fontWeight=on?'700':'400';g.group.parentNode.append(g.group)}}
render();
})();