(function(){
  var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};

  /* Statusdaten (freigegebener Stand) laden; ohne JavaScript bleibt der statische Text stehen.
     Sprache ergibt sich aus <html lang>; Englisch liest das Objekt "en" in status.json. */
  var EN=document.documentElement.lang==='en';
  var ST=EN?{owner_reported:'Own report',in_progress:'in progress',open:'open',failed:'test failed'}:{owner_reported:'Eigener Bericht',in_progress:'in Arbeit',open:'offen',failed:'Test fehlgeschlagen'};
  var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  function fmt(d){var m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(d||'');if(!m)return d;return EN?(+m[3])+' '+MON[+m[2]-1]+' '+m[1]:m[3]+'.'+m[2]+'.'+m[1]}
  function bind(k,v){if(typeof v!=='string')return;$$('[data-bind="'+k+'"]').forEach(function(e){e.textContent=v})}
  function list(id,items){var ul=$(id);if(!ul||!Array.isArray(items)||!items.length)return;ul.textContent='';items.forEach(function(t){var li=document.createElement('li');li.textContent=String(t);ul.appendChild(li)})}
  function miles(items,names){var ul=$('#ms');if(!ul||!Array.isArray(items)||!items.length)return;ul.textContent='';items.forEach(function(m){
    var li=document.createElement('li'),i=document.createElement('i'),n=document.createElement('span'),s=document.createElement('span');
    var st=ST[m.state]?m.state:'open';i.className='mk '+st;n.textContent=String((names&&names[m.id])||m.name);s.className='st';s.textContent=ST[st];
    li.appendChild(i);li.appendChild(n);li.appendChild(s);ul.appendChild(li)})}
  function hist(items,texts){var ol=$('#l-history');if(!ol||!Array.isArray(items)||!items.length)return;ol.textContent='';items.forEach(function(h,i){
    var li=document.createElement('li'),t=document.createElement('time'),s=document.createElement('span');
    t.setAttribute('datetime',String(h.date));t.textContent=fmt(h.date);s.textContent=String((texts&&texts[i])||h.text);
    li.appendChild(t);li.appendChild(s);ol.appendChild(li)})}
  fetch((EN?'../':'./')+'data/status.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error('status');return r.json()}).then(function(d){
    if(d.visibility!=='public'||d.approved!==true)return;
    var t=(EN&&d.en)?d.en:d;
    bind('title',t.title||d.title);bind('asof',fmt(d.as_of));bind('evidence',t.evidence||d.evidence);
    bind('meta',(EN?'As of ':'Stand: ')+fmt(d.as_of)+' \u00b7 '+(t.evidence||d.evidence));
    if(d.last_test){bind('lasttest',EN?(d.en&&d.en.last_test)||d.last_test.text:d.last_test.text);bind('lastdate',(EN?'Latest test':'Letzter Test')+' \u00b7 '+fmt(d.last_test.date))}
    var age=(Date.now()-Date.parse(d.as_of))/864e5;
    if(age>14){var mt=$('[data-bind="meta"]');if(mt){mt.classList.add('stale');mt.textContent+='__STALE__'}}
    list('#l-confirmed',t.confirmed||d.confirmed);list('#l-open',t.not_yet_verified||d.not_yet_verified);list('#l-issues',t.known_issues||d.known_issues);
    miles(d.milestones,EN&&d.en?d.en.milestones:null);
    hist(d.history,EN&&d.en?d.en.history:null);
  }).catch(function(){});

  /* Geräte filtern */
  var chips=$('#chips'),rows=$$('#devices tbody tr');
  if(chips){chips.hidden=false;chips.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;
    $$('button',chips).forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
    var f=b.getAttribute('data-f');rows.forEach(function(r){r.hidden=!(f==='all'||r.getAttribute('data-c')===f)})})}

  /* Menü (schmale Bildschirme) */
  var nav=$('#nav'),btn=$('.menu');
  function setMenu(o){if(!nav||!btn)return;nav.classList.toggle('open',o);btn.setAttribute('aria-expanded',o?'true':'false')}
  if(btn&&nav){btn.addEventListener('click',function(){setMenu(!nav.classList.contains('open'))});
    nav.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')setMenu(false)})}

  /* Navigation: aktuellen Abschnitt markieren */
  var links=$$('nav.main a'),map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(a){a.removeAttribute('aria-current')});var a=map[e.target.id];if(a){a.setAttribute('aria-current','true');}}})},{rootMargin:'-45% 0px -50% 0px'});
    Object.keys(map).forEach(function(id){var s=document.getElementById(id);if(s)io.observe(s)});
  }
})();
