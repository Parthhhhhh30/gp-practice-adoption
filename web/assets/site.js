/* Practice / Signal | no framework or paid service required. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const escape = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const percent = (n, digits=0) => n === null || n === undefined ? '—' : Number(n).toFixed(digits) + '%';
  const num = (n) => n === null || n === undefined ? '—' : Number(n).toLocaleString('en-GB');
  const name = (x) => escape(x);
  const request = async (path, options = {}) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    try {
      const response = await fetch(path, { ...options, signal: controller.signal, headers: { 'Accept': 'application/json', ...(options.body ? {'Content-Type':'application/json'} : {}) } });
      const data = await response.json();
      if (!response.ok) throw Error(data.detail || 'Service unavailable');
      return data;
    } finally { clearTimeout(timeout); }
  };
  let overview = null, source = null, activeCase = 'public', activeChoice = null, currentSection = 'today';
  let currentAccount = 'DEMO-001', currentFeedback = 'CALL-001', page = 0;
  const scenarios = {
    public: {
      title: 'A practice has a low phone-access score. What can you conclude?',
      description: 'The public survey records how respondents rated access. It cannot establish what software the practice uses, whether a product would help, or why access felt difficult.',
      label: 'PUBLIC SURVEY / UNVERIFIED CAUSE',
      choices: [
        'Flag the practice as a ready-made customer opportunity.',
        'Investigate the practice workflow before inferring any product requirement.',
        'Assume its current booking technology has failed.'
      ], target: 'practices', foot: 'A PUBLIC ACCESS SCORE IS NOT A CUSTOMER RECORD'
    },
    rollout: {
      title: 'A fictional customer is live, but activation is poor.',
      description: 'The simulated team has completed training, yet usage has stalled and a critical support issue is open. Should a second product be discussed already?',
      label: 'SIMULATED ROLLOUT / REAL READINESS RULES',
      choices: [
        'Start an expansion campaign to increase engagement.',
        'Resolve the support blocker and check actual use before expansion.',
        'Mark the project complete because onboarding attendance was recorded.'
      ], target: 'accounts', foot: 'TRAINING ATTENDANCE ≠ SUSTAINED ADOPTION'
    },
    feedback: {
      title: 'Practice staff keep reporting the same configuration problem.',
      description: 'Fictional support notes mention unclear routing and repeated workarounds. A drafted solution may be useful, but someone must validate the issue and decide what happens next.',
      label: 'FICTIONAL FEEDBACK / HUMAN-OWNED ACTION',
      choices: [
        'Let the assistant assign the next release priority.',
        'Preserve the original issue, capture evidence and assign a human review.',
        'Count a drafted reply as proof that the problem was fixed.'
      ], target: 'feedback', foot: 'DRAFTED RESPONSE ≠ RESOLVED ISSUE'
    }
  };
  const tabs = Array.from(document.querySelectorAll('.scenario-tab'));
  function drawScenario() {
    const c = scenarios[activeCase];
    $('scenario-question').textContent = c.title;
    $('scenario-description').textContent = c.description;
    $('scenario-label').textContent = c.label;
    $('scenario-footnote').textContent = c.foot;
    $('scenario-target').href = '/workbench#' + c.target;
    $('scenario-target').innerHTML = 'Open the evidence <span>↗</span>';
    $('scenario-choices').innerHTML = c.choices.map((o,i) => '<button type="button" class="choice" role="radio" aria-checked="' + (i===activeChoice) + '" data-option="' + i + '"><span class="letter">' + 'ABC'[i] + '</span><span>' + escape(o) + '</span></button>').join('');
    $('check-decision').disabled = activeChoice === null;
    $('decision-result').hidden = true;
    tabs.forEach(t => { const selected = t.dataset.case === activeCase; t.classList.toggle('active',selected); t.setAttribute('aria-selected',String(selected)); });
  }
  tabs.forEach(t=>t.addEventListener('click',()=>{activeCase=t.dataset.case;activeChoice=null;drawScenario();}));
  $('scenario-choices').addEventListener('click',e=>{const target=e.target.closest('[data-option]');if(!target)return;activeChoice=Number(target.dataset.option);drawScenario();});
  $('check-decision').addEventListener('click',async ()=>{
    if(activeChoice===null)return;
    const btn=$('check-decision');btn.disabled=true;btn.textContent='Checking with the live rule service…';
    try {
      const r=await request('/api/decision',{method:'POST',body:JSON.stringify({lens:activeCase,choice:'abc'[activeChoice]})});
      const node=$('decision-result');node.hidden=false;node.classList.toggle('no',!r.supported);
      node.innerHTML='<b>'+(r.supported?'SUPPORTED NEXT STEP':'NOT SUPPORTED BY THE EVIDENCE')+'</b>'+escape(r.reason)+'<br><small>Explanatory decision only. No customer record was changed.</small>';
    } catch(e) {const n=$('decision-result');n.hidden=false;n.classList.add('no');n.textContent='Decision service unavailable: '+e.message; }
    finally {btn.innerHTML='Check the judgement <span>↗</span>';btn.disabled=false;}
  });
  $('mobile-menu').addEventListener('click',()=>{const n=document.querySelector('.mastnav');const v=!n.classList.contains('open');n.classList.toggle('open',v);$('mobile-menu').setAttribute('aria-expanded',String(v));});
  document.querySelectorAll('.mastnav a').forEach(a=>a.addEventListener('click',()=>document.querySelector('.mastnav').classList.remove('open')));
  const article = (kicker,title,description) => '<div class="panel-kicker">'+escape(kicker)+'</div><h2 class="panel-title">'+escape(title)+'</h2><p class="panel-desc">'+escape(description)+'</p>';
  const tag = (s) => '<span class="pill '+(/Red|risk|Resolve/.test(s)?'risk':/Amber|Check/.test(s)?'warn':/Green|Ready/.test(s)?'good':'')+'">'+escape(s)+'</span>';
  const stat = (label,value,foot) => '<div class="stat"><span class="label">'+escape(label)+'</span><strong>'+escape(value)+'</strong><small>'+escape(foot)+'</small></div>';
  const note = (s) => '<div class="notice">'+escape(s)+'</div>';
  const brief = (s) => '<div class="status-message">'+escape(s)+'</div>';
  const accountSelect = (id) => '<div class="field"><label for="'+id+'">SIMULATED ACCOUNT</label><select id="'+id+'">'+overview.accounts.map(a=>'<option value="'+escape(a.id)+'" '+(a.id===currentAccount?'selected':'')+'>'+escape(a.name)+' · '+escape(a.id)+'</option>').join('')+'</select></div>';
  const getAccount = () => overview.accounts.find(x=>x.id===currentAccount) || overview.accounts[0];
  const meter = (n,kind='') => '<div class="meter '+kind+'"><i style="width:'+Math.round(Math.min(100,Math.max(0,Number(n)||0)))+'%"></i></div>';
  const formatIssue = (a) => a.critical_issue ? 'Critical issue open' : a.activation ? 'No critical blocker' : 'Activation incomplete';
  function today() {
    const o=overview;
    return article('01 / THE OPERATOR DESK','What needs attention first?','A deterministic work queue puts simulated support and adoption risks ahead of expansion. Nothing here represents a real practice relationship.')
      +'<div class="stat-grid">'+stat('FICTIONAL ACCOUNTS',o.totals.accounts,'Fixed demo portfolio')+stat('ACCOUNTS AT RISK',o.totals.risk,'Onboarding or adoption red')+stat('ACTIVATED',o.totals.activated,'Simulated activation flags')+stat('FEEDBACK RECORDS',o.totals.feedback,'Fictional call notes')+'</div>'
      +'<div class="panel-columns"><div class="panel-card"><h3>Priority queue</h3>'+o.priority.slice(0,9).map(x=>'<div class="list-row"><div><b>'+escape(x.name)+'</b><span>'+escape(x.id)+' · Onboarding '+escape(x.onboarding)+' / adoption '+escape(x.health)+'</span></div>'+tag(x.tag)+'</div>').join('')+'</div><div><div class="panel-card"><h3>The operating judgement</h3><p>Do not interpret a rollout as successful just because training happened. Check activation, outstanding issues and sustained usage separately. If a customer has a critical blocker, investigate that before expansion.</p></div><div class="panel-card"><h3>Next action</h3><p>Choose any fictional account in <b>Account readiness</b> to inspect its decision rule and support status.</p><button class="plain-button" data-go="accounts">Examine account evidence ↗</button></div></div></div>'
      +note('Every account, name, product subscription and result in this view is fictional. The priority calculations execute in Python against seeded records.');
  }
  function practices() {
    return article('02 / PUBLIC SOURCE','Explore practice access evidence','Search the official practice-level 2026 GP Patient Survey. Lower-than-median access is a descriptive signal, never proof of a supplier relationship or a reason to sell a product.')
      +'<div class="filter-bar"><div class="field"><label for="practice-q">PRACTICE / HEALTH SYSTEM</label><input id="practice-q" placeholder="Search practice or ICS…"></div><div class="field"><label for="practice-signal">OBSERVED SIGNAL</label><select id="practice-signal"><option value="all">All reported practices</option><option value="phone">Below-median phone ease</option><option value="digital">Below-median digital ease</option><option value="phone-digital">Below phone / at-or-above website median</option></select></div><button class="plain-button" id="practice-search">Inspect records ↗</button></div><div id="public-panel" class="loader"><span class="spin"></span> Contacting the published data source…</div>';
  }
  function accountPane() {
    const a=getAccount();
    const next=a.critical_issue?'Resolve critical support issue; record the owner and retest.':!a.activation?'Clarify the incomplete activation step before moving to expansion.':a.health==='Red'?'Investigate the downward usage pattern and customer friction.':a.expansion==='Ready for discovery'?'Validate the value story with the customer before proposing another product.':'Monitor usage and seek customer feedback before changing scope.';
    return article('03 / FICTIONAL ROLLOUT','Is the account ready?','This is a simulated customer operations view. All statuses are computed by the same deterministic Python rules as the original Streamlit version.')
      +'<div class="filter-bar">'+accountSelect('account-select')+'</div>'
      +'<div class="stat-grid">'+stat('ONBOARDING',a.onboarding,'Based on setup and blockers')+stat('ADOPTION',a.health,'Rule-derived status')+stat('EXISTING ADOPTION',percent(a.existing_adoption),'Seeded fictional measure')+stat('SETUP AGE',a.days_since_setup+' days','Simulated timeline')+'</div>'
      +'<div class="panel-columns"><div class="panel-card"><h3>'+escape(a.name)+'</h3><p>'+escape(a.goal)+' · '+escape(a.product)+'</p>'
      +'<div class="list-row"><div><b>Activation</b><span>Account activation checks</span></div>'+tag(a.activation?'Complete':'Incomplete')+'</div>'
      +'<div class="list-row"><div><b>Support</b><span>Critical issue flag</span></div>'+tag(formatIssue(a))+'</div>'
      +'<div class="list-row"><div><b>Expansion readiness</b><span>Calculated separately from adoption</span></div>'+tag(a.expansion)+'</div>'
      +'<p>'+escape(a.expansion_reasons?.join(' · ')||'No additional reasons recorded')+'</p></div>'
      +'<div class="panel-card"><h3>What should happen next?</h3><p>'+escape(next)+'</p><button class="plain-button" data-go="adoption">Inspect adoption evidence ↗</button><p class="muted">Advice is derived from the displayed fictional state. No change is sent to a customer.</p></div></div>';
  }
  function adoptionPane() {
    const a=getAccount();
    return article('04 / CUSTOMER VALUE','Used is not the same as adopted.','Training completion, short-term activity and sustained value are different things. These indicators come from seeded fictional data, not NHS reporting or a commercial implementation.')
      +'<div class="filter-bar">'+accountSelect('adoption-select')+'</div><div class="stat-grid">'
      +stat('ADOPTION HEALTH',a.health,'Deterministic rule')+stat('TIME TO FIRST VALUE',a.time_to_value+' days','Simulated')+stat('ROUTED REQUESTS',percent(a.routed_pct,1),'Simulated')+stat('STAFF TIME',a.time_saving+' min','Illustrative weekly saving')+'</div>'
      +'<div class="panel-columns"><div class="panel-card"><h3>Usage compared with expectation</h3><b>'+percent(a.usage_ratio*100)+'</b>'+meter(a.usage_ratio*100,a.health==='Red'?'risky':'healthy')+'<p>Four-week change: <b>'+ (a.trend>0?'+':'') +a.trend.toFixed(1)+'%</b>. Weekly requests: <b>'+num(a.weekly_requests)+'</b>.</p><p>These numbers are deterministic fixtures for demonstrating a review process. They are not measured customer outcomes.</p></div><div class="panel-card"><h3>Questions before a handover</h3><p>Can staff complete routine tasks? Are support issues resolved? Is adoption improving for the right reason? Can someone explain where usage figures came from?</p><p>A handover should follow evidence of a workable service, not a fabricated green status.</p></div></div>';
  }
  function feedbackPane() {
    const f=overview.feedback.find(x=>x.id===currentFeedback)||overview.feedback[0];
    return article('05 / CUSTOMER VOICE','Keep the issue attached to the evidence.','Fictional practice feedback contains repeated concerns around configuration, onboarding, support and reporting. Preserve original wording before proposing changes.')
      +'<div class="stat-grid">'+stat('FICTIONAL CALL NOTES',overview.feedback.length,'Synthetic examples')+stat('RECURRING THEMES',overview.themes.length,'Aggregated by Python rules')+stat('AI CALLS',0,'Drafts here are deterministic')+stat('REAL CUSTOMERS',0,'No supplier relationships')+'</div>'
      +'<div class="panel-columns"><div class="panel-card"><h3>Recurring themes</h3>'+overview.themes.map(x=>'<div class="list-row"><div><b>'+escape(x.topic)+'</b><span>Fictional feedback category</span></div>'+tag(x.count+' mentions')+'</div>').join('')+'</div><div class="panel-card"><h3>Open a call note</h3><div class="field"><label for="feedback-select">SOURCE NOTE</label><select id="feedback-select">'+overview.feedback.map(x=>'<option value="'+escape(x.id)+'" '+(x.id===currentFeedback?'selected':'')+'>'+escape(x.id)+' · '+escape(x.topic)+'</option>').join('')+'</select></div><blockquote class="feedback-quote">'+escape(f.text)+'</blockquote><button class="plain-button" id="draft-ticket">Create reviewable ticket ↗</button><div id="ticket-result" role="status"></div></div></div>'+note('Ticket drafts are built from the exact fictional note using deterministic rules. No Gemini API inference or external ticket creation occurs.');
  }
  function playbookPane() {
    const rows=[
      ['01','Understand','Start with the practice’s actual workflow and documented access signals.'],
      ['02','Configure','Identify owners, required settings, acceptance criteria and unresolved assumptions.'],
      ['03','Validate','Check sources, permissions, expected outcomes and failed tests before go-live.'],
      ['04','Enable','Train for real exceptions and provide routes for help, not just an attendance list.'],
      ['05','Review','Measure actual use against agreed goals; keep observations separate from planned interventions.'],
      ['06','Improve','Use recurring support evidence to assign the next process change to a human owner.']];
    return article('06 / REPEATABLE DELIVERY','What would you change next time?','A reusable playbook distils recurring friction into implementable steps. It is a proposed operating model—not a claim of NHS-approved procedures.')
      +'<div class="flow-steps">'+rows.map(x=>'<div class="flow-step"><span>'+escape(x[0])+' / OPERATING STEP</span><h3>'+escape(x[1])+'</h3><p>'+escape(x[2])+'</p></div>').join('')+'</div>'
      +'<div class="panel-columns"><div class="panel-card"><h3>Evidence-led improvements</h3>'+overview.themes.map(x=>'<div class="list-row"><div><b>'+escape(x.topic)+'</b><span>'+x.count+' fictional occurrences</span></div>'+tag('Review')+'</div>').join('')+'</div><div class="panel-card"><h3>Scope boundary</h3><p>Clinical migration, governance approvals, security controls and patient safety require qualified practitioners and genuine clinical evidence. This project is intentionally limited to simulated customer operations.</p></div></div>';
  }
  async function publicQuery(){
    const el=$('public-panel'); if(!el)return;
    const q=encodeURIComponent(($('practice-q')?.value||'').trim()), signal=$('practice-signal')?.value||'all';
    el.innerHTML='<div class="loader"><span class="spin"></span> Loading public practice observations…</div>';
    try{
      const d=await request('/api/practices?q='+q+'&signal='+signal+'&offset='+(page*24)+'&limit=24');
      if(!d.available){el.innerHTML=brief(d.message);return;}
      if(!d.records.length){el.innerHTML=brief('No matching practice rows. Change your filters and search again.');return;}
      el.innerHTML='<div class="stat-grid">'+stat('MATCHING ROWS',num(d.count),'Matches current search')+stat('TOTAL SOURCE ROWS',num(d.total),'Public practice records')+stat('MEDIAN PHONE EASE',percent(d.medians.phone_easy_pct),'Practice-level median')+stat('MEDIAN WEBSITE EASE',percent(d.medians.website_easy_pct),'Practice-level median')+'</div>'
        +'<div class="table-scroll"><table><thead><tr><th>Practice</th><th>ICS</th><th>Phone easy</th><th>Website easy</th><th>NHS App easy</th></tr></thead><tbody>'
        +d.records.map(x=>'<tr><td><b>'+escape(x.name)+'</b><br><span class="muted">'+escape(x.code)+'</span></td><td>'+escape(x.ics)+'</td><td>'+percent(x.phone)+'</td><td>'+percent(x.website)+'</td><td>'+percent(x.app)+'</td></tr>').join('')
        +'</tbody></table></div><div class="pagination"><span>Showing '+num(page*24+1)+'–'+num(Math.min(page*24+24,d.count))+' of '+num(d.count)+'</span><div><button id="page-prev" '+(page===0?'disabled':'')+'>← Previous</button> <button id="page-next" '+((page+1)*24>=d.count?'disabled':'')+'>Next →</button></div></div>'+note(d.note);
    }catch(e){el.innerHTML=brief('The public feed could not be loaded. '+e.message+' No missing data was replaced with synthetic results.');}
  }
  async function render(section){
    currentSection=section;
    document.querySelectorAll('.workspace-nav button').forEach(x=>x.classList.toggle('active',x.dataset.section===section));
    history.replaceState(null,'','/workbench#'+section);
    const panel=$('workspace-panel');
    if(!overview){panel.innerHTML='<div class="loader"><span class="spin"></span> Loading fictional case evidence…</div>';return;}
    switch(section){
      case 'today':panel.innerHTML=today();break;
      case 'practices':panel.innerHTML=practices();page=0;await publicQuery();break;
      case 'accounts':panel.innerHTML=accountPane();break;
      case 'adoption':panel.innerHTML=adoptionPane();break;
      case 'feedback':panel.innerHTML=feedbackPane();break;
      case 'playbook':panel.innerHTML=playbookPane();break;
    }
  }
  $('workspace-panel').addEventListener('click',async e=>{
    const go=e.target.closest('[data-go]');
    if(go){await render(go.dataset.go);return;}
    if(e.target.closest('#practice-search')){page=0;await publicQuery();return;}
    if(e.target.closest('#page-prev')){page=Math.max(0,page-1);await publicQuery();return;}
    if(e.target.closest('#page-next')){page+=1;await publicQuery();return;}
    if(e.target.closest('#draft-ticket')){
      const el=$('ticket-result');el.textContent='Creating draft…';
      try{const d=await request('/api/ticket',{method:'POST',body:JSON.stringify({feedback_id:currentFeedback})});
        el.innerHTML='<div class="ticket"><b>'+escape(d.type)+'</b><p><strong>'+escape(d.category)+'</strong> / '+escape(d.reference)+'</p><p>'+escape(d.source)+'</p><p><strong>Proposed next step:</strong> '+escape(d.next_step)+'</p><p><strong>Owner:</strong> '+escape(d.proposed_owner)+'</p><p>'+escape(d.status)+' · '+escape(d.generated_by)+'</p></div>';
      }catch(err){el.textContent='Draft unavailable: '+err.message;}
    }
  });
  $('workspace-panel').addEventListener('change',async e=>{
    if(e.target.id==='account-select'||e.target.id==='adoption-select'){currentAccount=e.target.value;render(currentSection);}
    if(e.target.id==='feedback-select'){currentFeedback=e.target.value;render('feedback');}
  });
  $('workspace-panel').addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.id==='practice-q'){$('practice-search')?.click();}});
  document.querySelectorAll('.workspace-nav button').forEach(b=>b.addEventListener('click',()=>render(b.dataset.section)));
  function openWorkspace() {
    $('story-view').hidden=true;$('workbench-view').hidden=false;
    const hash=location.hash.replace('#','').toLowerCase();
    const chosen=['today','practices','accounts','adoption','feedback','playbook'].includes(hash)?hash:'today';
    render(chosen);
  }
  const onWorkbench=window.location.pathname.startsWith('/workbench');
  if(onWorkbench)openWorkspace();
  else{$('story-view').hidden=false;$('workbench-view').hidden=true;}
  drawScenario();
  async function init(){
    const live=await Promise.allSettled([request('/api/health'),request('/api/overview')]);
    if(live[0].status==='fulfilled'){$('api-led').classList.add('ok');$('workbench-state').textContent='Live / ready';}
    else $('workbench-state').textContent='API unavailable';
    if(live[1].status==='fulfilled'){overview=live[1].value;$('demo-count').textContent=String(overview.totals.accounts).padStart(2,'0');
      if(onWorkbench){const chosen=location.hash.replace('#','')||'today';render(['today','practices','accounts','adoption','feedback','playbook'].includes(chosen)?chosen:'today');}
    } else if(onWorkbench){$('workspace-panel').innerHTML=brief('The operations API is unavailable. Try again after refreshing. No synthetic success is displayed.');}
    if(!onWorkbench){
      try{const data=await request('/api/practices?limit=1');
        if(data.available){$('real-count').textContent=num(data.total);$('real-median').textContent=percent(data.medians.phone_easy_pct);
          $('source-note').textContent='GP Patient Survey 2026 / live official-source query · Practice-level percentages; no personal or clinical records.';}
        else{$('real-count').textContent='Unavailable';$('real-median').textContent='—';$('source-note').textContent=data.message;}
      }catch(e){$('real-count').textContent='Unavailable';$('source-note').textContent='Public source unreachable in this session. No estimates have been substituted.';}
    }
  }
  init();
  window.addEventListener('hashchange',()=>{if(onWorkbench){const s=location.hash.slice(1);if(['today','practices','accounts','adoption','feedback','playbook'].includes(s))render(s);}});
})();
