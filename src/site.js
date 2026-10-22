(function(){var d=document.documentElement;d.classList.add('js');
var still=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
if(!still&&'IntersectionObserver' in window){d.classList.add('motion');
var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -6% 0px'});
document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});}
var bar=document.getElementById('sticky'),req=document.getElementById('request');
if(bar&&req&&'IntersectionObserver' in window){new IntersectionObserver(function(es){bar.classList.toggle('away',es[0].isIntersecting);},{threshold:0.05}).observe(req);}
})();
