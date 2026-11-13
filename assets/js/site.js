(function(){
  var $=function(s,r){return (r||document).querySelector(s)}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};

  /* Alte Sprungmarken der früheren Ein-Seiten-Fassung (z. B. /#stand, /#f12, /#u3) auf die neue Seite umleiten.
     Die Zuordnung Abschnitt -> Seite setzt Hugo beim Bauen ein; auf Unterseiten ist sie leer. */
  var MOVED=__MOVED__, h=location.hash.slice(1);
  if(h&&!document.getElementById(h)){
    var t=MOVED[h]||(/^f\d+$/.test(h)&&MOVED.befunde)||(/^u\d+$/.test(h)&&MOVED.umbau)||(/^v-\d/.test(h)&&MOVED.stand);
    if(t){location.replace(t+'#'+h);return}
  }

  /* Der Projektstand steht fertig im HTML (aus data/status.json gebaut). Hier wird nur beim Aufruf geprüft,
     ob er älter als 14 Tage ist, und das sichtbar markiert. */
  $$('[data-asof]').forEach(function(e){
    var age=(Date.now()-Date.parse(e.getAttribute('data-asof')))/864e5;
    if(age>14){e.classList.add('stale');if(e.hasAttribute('data-stale-append'))e.textContent+='__STALE__'}
  });

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
})();
