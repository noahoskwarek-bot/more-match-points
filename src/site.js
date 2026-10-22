(function(){var d=document.documentElement;d.classList.add('js');
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
if(!still&&'IntersectionObserver' in window){d.classList.add('motion');
var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -6% 0px'});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});}
var bar=document.getElementById('sticky'),req=document.getElementById('request');
if(bar&&req&&'IntersectionObserver' in window){new IntersectionObserver(function(es){bar.classList.toggle('away',es[0].isIntersecting);},{threshold:0.05}).observe(req);}
/* header nav: disclosure dropdowns (desktop) + hamburger panel (mobile). Without JS the plain links stay. */
var top=document.getElementById('top'),burger=top&&top.querySelector('.burger'),nav=document.getElementById('site-nav');
if(!top||!burger||!nav)return;
var wide=window.matchMedia?matchMedia('(min-width:980px)'):{matches:true};
var dds=[].slice.call(top.querySelectorAll('.dd'));
function btn(dd){return dd.querySelector('.dd-btn');}
function setDD(dd,open){dds.forEach(function(o){var on=open&&o===dd;o.classList.toggle('open',on);btn(o).setAttribute('aria-expanded',on?'true':'false');});}
function openDD(){for(var i=0;i<dds.length;i++){if(dds[i].classList.contains('open'))return dds[i];}return null;}
function menuOpen(){return top.classList.contains('open');}
function setMenu(open,focusBack){top.classList.toggle('open',open);burger.setAttribute('aria-expanded',open?'true':'false');
burger.setAttribute('aria-label',open?'Close menu':'Menu');d.classList.toggle('nav-lock',open);
if(!open){setDD(null,false);if(focusBack)burger.focus();}}
dds.forEach(function(dd){var a=dd.querySelector('.dd-link'),b=btn(dd);a.hidden=true;b.hidden=false;
b.addEventListener('click',function(){setDD(dd,b.getAttribute('aria-expanded')!=='true');});
b.addEventListener('keydown',function(ev){if(ev.key==='ArrowDown'){ev.preventDefault();setDD(dd,true);var f=dd.querySelector('.dd-menu a');if(f)f.focus();}});
dd.addEventListener('keydown',function(ev){if(ev.target===b||!wide.matches||(ev.key!=='ArrowDown'&&ev.key!=='ArrowUp'))return;
var ls=[].slice.call(dd.querySelectorAll('.dd-menu a')),i=ls.indexOf(document.activeElement);if(i<0)return;ev.preventDefault();
ls[(i+(ev.key==='ArrowDown'?1:ls.length-1))%ls.length].focus();});
dd.addEventListener('focusout',function(ev){if(wide.matches&&ev.relatedTarget&&!dd.contains(ev.relatedTarget))setDD(dd,false);});});
burger.hidden=false;
burger.addEventListener('click',function(){setMenu(!menuOpen(),false);});
document.addEventListener('keydown',function(ev){
if(ev.key==='Escape'||ev.key==='Esc'){var o=openDD();
if(menuOpen()&&!wide.matches){setMenu(false,true);}else if(o){setDD(null,false);btn(o).focus();}return;}
if(ev.key==='Tab'&&menuOpen()&&!wide.matches){var f=[burger].concat([].slice.call(nav.querySelectorAll('a,button')).filter(function(x){return x.offsetParent!==null;}));
var i=f.indexOf(document.activeElement);
if(ev.shiftKey&&i<=0){ev.preventDefault();f[f.length-1].focus();}else if(!ev.shiftKey&&i===f.length-1){ev.preventDefault();f[0].focus();}}});
document.addEventListener('click',function(ev){var o=openDD();if(o&&wide.matches&&!o.contains(ev.target))setDD(null,false);});
nav.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('a');if(a&&menuOpen())setMenu(false,false);});
var mq=function(){setMenu(false,false);};if(wide.addEventListener)wide.addEventListener('change',mq);else if(wide.addListener)wide.addListener(mq);
})();
