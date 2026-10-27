/* Jam Archive v0.4 - source-first research queue, not a publication or approval interface */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const safe=x=>String(x??'').replace(/[&<>"']/g,k=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[k]));
const research=db.research||{items:[],summary:{pending:0,approved:0,rejected:0,demo:0}};
const items=research.items||[];
function display(){
  let filter=$('research-filter').value;
  let q=$('research-find').value.trim().toLowerCase();
  const view=items.filter(x=>(filter==='all'||x.candidate_type===filter||x.status===filter||filter==='demo'&&x.demo)&&(!q||[x.artist,x.title,x.observed_date,x.venue,x.reason].join(' ').toLowerCase().includes(q)));
  $('research-list').innerHTML=view.length?view.map(x=>`<article class="research-item">
    <div class="history-card-top"><div><span class="eyebrow">${safe(x.provider)} / ${safe(x.candidate_type)} / ${safe(x.status)}</span><h3>${safe(x.artist)} ${x.observed_date?`· ${safe(x.observed_date)}`:''}</h3></div><span class="badge ${x.demo?'gold':''}">${x.demo?'SYNTHETIC DEMO':'SOURCE OBSERVATION'}</span></div>
    <p>${safe(x.title)}</p><p class="note">${safe(x.reason)}</p>
    ${x.proposed_show_id?`<p class="note"><strong>Potential show match:</strong> ${safe(x.proposed_show_id)} (not verified)</p>`:''}
    ${x.venue?`<p class="note">Reported venue: ${safe(x.venue)}</p>`:''}
    <a class="outlink" href="${safe(x.source_url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>
    <div class="tiny">Review ID: <code>${safe(x.id)}</code> · First seen ${safe(x.first_seen.slice(0,10))}</div>
   </article>`).join(''):'<div class="empty">No collected observations in this filter. An empty research queue does not imply there are no shows or recordings.</div>';
  $('research-visible').textContent=`Showing ${view.length} of ${items.length} observations`;
}
$('research-filter').addEventListener('change',display);$('research-find').addEventListener('input',display);
$('research-pending').textContent=research.summary.pending||0;
$('research-demo').textContent=research.summary.demo||0;
$('research-reviewed').textContent=(research.summary.approved||0)+(research.summary.rejected||0);
$('research-nav-count').textContent=research.summary.pending||0;
$('research-datestamp').textContent=(research.generated_at||'Never').replace('T',' ').slice(0,19)+' UTC';
display();
})();
