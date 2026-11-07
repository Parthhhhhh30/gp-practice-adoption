import {seeds,fresh,diagnostic,validateEscalation,canClose,checkResponse,baseline,evaluateBaseline,nowIso,MODEL_VERSION} from './rules.mjs';
const $=x=>document.getElementById(x), esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const when=s=>new Date(s).toLocaleString('en-GB',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'});
let db=null,state=fresh(),chosen='CW-204',tab='investigate',feedback='',aiEnabled=false;
function openDB(){return new Promise((ok,bad)=>{let r=indexedDB.open('casework-v2-local',1);r.onupgradeneeded=()=>r.result.createObjectStore('cases');r.onsuccess=()=>ok(r.result);r.onerror=()=>bad(r.error)})}
function read(){return new Promise((ok,bad)=>{let r=db.transaction('cases','readonly').objectStore('cases').get('workspace');r.onsuccess=()=>ok(r.result);r.onerror=()=>bad(r.error)})}
function write(){return new Promise((ok,bad)=>{let r=db.transaction('cases','readwrite').objectStore('cases').put(state,'workspace');r.onsuccess=()=>ok();r.onerror=()=>bad(r.error)})}
async function save(){if(db)await write();$('save-status').textContent=db?'AUTOSAVED / BROWSER LOCAL':'UNSAVED / SESSION ONLY'}
const current=()=>state.cases.find(c=>c.id===chosen);
function log(c,title,details){c.history.unshift({at:nowIso(),action:title,details});}
async function change(c,title,details){log(c,title,details);feedback='';render();await save();}
function notice(s){feedback=s;render()}
function button(action,label,cls=''){return '<button class="btn '+cls+'" data-action="'+action+'">'+label+'</button>'}
function field(id,title,content,textarea=true){return '<div class="form-field"><label for="'+id+'">'+title+'</label>'+(textarea?'<textarea id="'+id+'">'+esc(content||'')+'</textarea>':'<input id="'+id+'" value="'+esc(content||'')+'">')+'</div>'}
function card(x){return '<div class="card">'+x+'</div>'}
function heading(code,title,desc){return '<span class="panel-eyebrow">'+code+'</span><h3 class="panel-title">'+title+'</h3><p class="panel-intro">'+desc+'</p>'}
function diagnosticHTML(d){return '<div class="evidence-block">'+d.lines.map(esc).join('<br>')+'<br><br><strong>'+esc(d.label)+'</strong></div><p>'+esc(d.guidance)+'</p>'}
function investigation(c){
 let d=c.diagnostics.at(-1),now=diagnostic(c),fix=c.kind==='login'?'Refresh fictional session':c.kind==='graphql'?'Correct missing variable':'Refresh fictional import snapshot';
 return heading('01 / INVESTIGATE','Test the failure before choosing the answer.','The test calls a fictional server endpoint. Inspect the network response; HTTP success can still include an application error.')
 +card('<div class="meta">FICTIONAL CUSTOMER MESSAGE</div><p>“'+esc(c.customer)+'”</p><p><b>Expected:</b> '+esc(c.expected)+'</p>')
 +'<div class="two-col">'+card('<h3>Controlled test environment</h3><p>Inspect and reproduce. Make a change, then retest.</p>'+button('diagnose','Run diagnostic ↗')+(c.kind==='legal'?'':button('fix',fix,'secondary'))+(c.kind==='documents'?button('security','Simulate possible data exposure','warn'):''))+card('<h3>Record your investigation</h3>'+field('note','Findings, evidence and next steps',c.note)+button('note','Save evidence notes','secondary'))+'</div>'
 +(d?card('<small>LATEST TEST / '+when(d.at)+'</small><h3>'+(d.pass?'PASS':'FAIL')+'</h3>'+diagnosticHTML(d)+(d.pass?button('verify','Record verified outcome'):'<p class="meta">Fix or escalate before marking resolved.</p>')):card('<h3>No test executed yet</h3><p>Run the controlled server request to inspect the evidence.</p>'))
 +(c.kind==='legal'?card('<h3>Patent-domain boundary</h3><p>Support cannot attest to the legality of an AI-generated argument. Preserve the concern and route for specialist review.</p>'):'');
}
function response(c){
 const examples={login:'Thank you for reporting the sign-in loop. I am checking the affected session and will confirm the outcome after testing. Please do not send your password.',graphql:'Thank you for flagging that your settings did not persist. I have reproduced the issue and am checking the update request before confirming a fix.',documents:'Thank you for raising the missing document update. I am comparing the imported copy with the source version and will share what the evidence confirms.',legal:'Thank you for identifying the unverified reference. I cannot confirm the legal correctness of the draft; a qualified patent specialist needs to review the relevant material.'};
 return heading('02 / COMMUNICATION','Write a precise customer update.','The operator owns the response. AI critique is optional, limited and never sends the message.')
 +card('<p><b>Incoming:</b> '+esc(c.customer)+'</p>'+field('reply','Customer-facing draft',c.reply||examples[c.kind])+button('approve','Check and approve draft')+button('ai','Request live AI critique','secondary')+'<p class="meta">UNSENT · NEVER FORWARDED TO A REAL CUSTOMER</p>')
 +(c.replyApproved?card('<h3>Locally approved</h3><p>The draft is in the case history. No outbound message was transmitted.</p>'):'')
 +(state.aiRuns.filter(x=>x.id===c.id).length?card('<h3>Model critique (untrusted suggestion)</h3><p>'+esc(JSON.stringify(state.aiRuns.filter(x=>x.id===c.id).at(-1).output))+'</p>'):'');
}
function escalate(c){
 let recommended=c.fault.security?'Security':c.kind==='legal'?'Patent-domain specialist':c.kind==='graphql'?'Engineering':'Customer support';
 return heading('03 / ESCALATION','Give specialists the evidence to act.','A partial escalation creates more work. A security concern must not wait for a standard support checklist.')
 +card('<div class="form-field"><label for="target">Appropriate owner</label><select id="target">'+['Customer support','Engineering','Patent-domain specialist','Security'].map(x=>'<option'+(x===recommended?' selected':'')+'>'+x+'</option>').join('')+'</select></div>'+field('reason','Expected/observed result, reproduction and requested action','')+'<p class="meta">EXECUTED TESTS: '+c.diagnostics.length+' · SAVED EVIDENCE: '+esc(c.note||'None')+'</p>'+button('route','Validate and record handover'))
 +(c.routing?card('<h3>Recorded handover</h3><p>'+esc(c.routing.target)+' / '+esc(c.routing.priority)+'</p><p>'+esc(c.routing.reason)+'</p><small>LOCAL DEMO ONLY · NOT SENT</small>'):'');
}
function knowledge(c){
 let matching=state.articles.filter(a=>a.kind===c.kind&&a.approved);
 return heading('04 / KNOWLEDGE','A resolution is useful twice when it is documented.','Only approved simulation articles are suggested. No official vendor guidance or client data is implied.')
 +card('<h3>Approved relevant articles</h3>'+(matching.length?matching.map(a=>'<div class="kb-item"><small>'+esc(a.id)+' / '+esc(a.from)+'</small><h4>'+esc(a.title)+'</h4><ol>'+a.steps.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ol></div>').join(''):'<p>No approved article for this case type yet.</p>'))
 +card('<h3>Write a reusable resolution</h3><p>Publishing requires a verified technical resolution, supporting notes and a reviewed customer response.</p>'+field('article-name','Article title','',false)+field('article-steps','Steps, one per line','')+button('publish','Publish locally approved article'))
 +card('<h3>Routing evaluation</h3><p>Run 8 deterministic test cases. These do not test an LLM.</p>'+button('eval','Run evaluation','secondary')+'<div id="eval-output"></div>');
}
function activity(c){
 const gate=canClose(c);
 return heading('05 / AUDIT HISTORY','What actually happened?','Actions and evidence persist in your browser until you reset this isolated fictional casebook.')
 +card('<div class="timeline">'+c.history.map(e=>'<div class="event"><span>'+when(e.at)+'</span><b>'+esc(e.action)+'</b><p>'+esc(e.details)+'</p></div>').join('')+'</div>')
 +card('<h3>Closure gate: '+(gate.ok?'READY':'NOT READY')+'</h3>'+gate.problems.map(x=>'<p class="notice">'+esc(x)+'</p>').join('')+button('close','Attempt verified closure')+button('reopen','Reopen investigation','secondary'));
}
function render(){
 let c=current();$('case-count').textContent='0'+state.cases.length;
 $('case-list').innerHTML=state.cases.map(x=>'<button data-case="'+x.id+'" class="'+(x.id===chosen?'active':'')+'"><small>'+x.id+' / '+esc(x.urgency)+'</small><b>'+esc(x.title)+'</b><span>'+esc(x.state)+'</span></button>').join('');
 $('case-title').textContent=c.title;$('case-kicker').textContent=c.id+' / '+c.channel.toUpperCase()+' / FICTIONAL';
 $('case-intro').textContent=c.customer;$('case-status').textContent=c.state;$('rail-id').textContent=c.id;
 $('case-status').className='status-badge'+(c.state==='Resolved'?' good':c.fault.security?' risk':'');
 $('case-facts').innerHTML=[['FICTIONAL CUSTOMER',c.person+' / '+c.firm],['CHANNEL',c.channel],['REPORTED IMPACT',c.impact],['CURRENT OWNER',c.routing?.target||'Customer support'],['VERIFICATION',c.verified?'Recorded':'Not completed']].map(a=>'<div class="fact"><small>'+a[0]+'</small><strong>'+esc(a[1])+'</strong></div>').join('');
 document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x.dataset.tab===tab));
 $('tab-panel').innerHTML={investigate:investigation,respond:response,escalate,knowledge,history:activity}[tab](c)+(feedback?'<div class="notice" role="status">'+esc(feedback)+'</div>':'');
}
async function action(key){
 let c=current();feedback='';
 if(key==='note'){c.note=$('note').value.trim();await change(c,'Investigation evidence recorded',c.note.slice(0,280));return}
 if(key==='diagnose'){
  // The diagnostic now makes a genuine request to a bounded fictional service.
  // No fallback can masquerade as a server response.
  let d;
  try {
    const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),12000);
    try {
      if(c.kind==='graphql'){
        const variables={settings:{review:true}};
        if(!c.fault.missingId)variables.draftId='demo_42';
        const response=await fetch('/api/graphql',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({operationName:'UpdateDraftSettings',variables})});
        const payload=await response.json();
        if(!response.ok||!payload.simulation)throw Error('Fictional GraphQL service unavailable.');
        const passed=Boolean(payload.data?.updateDraftSettings?.success)&&!payload.errors?.length;
        d={pass:passed,category:'Client/API',label:passed?'MUTATION_OK':'GRAPHQL_VALIDATION_ERROR',
        lines:['POST /api/graphql → HTTP '+response.status,'operation: UpdateDraftSettings','variables: '+JSON.stringify(variables),
        passed?'response.data.updateDraftSettings.success: true':'response.errors: '+JSON.stringify(payload.errors||[])],
        guidance:passed?'Fictional GraphQL mutation accepted and returned the updated value.':'HTTP 200 did not mean mutation success. Investigate the returned GraphQL errors.',
        simulation:true,executedOn:'casework-graphql-server'};
      }else{
        const response=await fetch('/api/lab',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:c.kind,fault:c.fault})});
        const payload=await response.json();
        if(!response.ok||payload.simulation!==true||typeof payload.pass!=='boolean'||!Array.isArray(payload.lines))throw Error('Controlled investigation service unavailable.');
        d=payload;
      }
    }finally{clearTimeout(timer)}
  }catch(e){notice('Live diagnostic failed: '+e.message+' No local result was substituted.');return;}
  c.diagnostics.push({...d,at:nowIso()});c.verified=false;
  if(c.state==='New')c.state='Investigating';
  await change(c,'Server diagnostic '+(d.pass?'passed':'failed'),d.lines.join(' | ').slice(0,600));
  return;
 }
 if(key==='fix'){
  if(c.kind==='legal'||c.fault.security){notice('This issue requires qualified specialist review.');return}
  if(c.kind==='login')c.fault.expired=false;if(c.kind==='graphql')c.fault.missingId=false;if(c.kind==='documents')c.fault.stale=false;
  c.verified=false;c.state='Fix pending verification';await change(c,'Controlled configuration changed','Rerun the diagnostic; a configuration change alone is not proof of resolution.');return;
 }
 if(key==='security'){c.fault.security=true;c.verified=false;c.state='Investigating';await change(c,'Possible information exposure simulated','Stop routine changes and route to Security.');return}
 if(key==='verify'){
  if(!c.diagnostics.at(-1)?.pass||c.kind==='legal'||c.fault.security){notice('No verified safe technical outcome is available.');return}
  c.verified=true;c.state='Fix pending verification';await change(c,'Successful retest recorded','Latest diagnostic passed with current configuration.');return;
 }
 if(key==='approve'){
  const v=$('reply').value.trim(),problems=checkResponse(v);if(problems.length){notice(problems.join(' '));return}
  c.reply=v;c.replyApproved=true;await change(c,'Written customer update reviewed','Human-approved local draft; not transmitted.');return
 }
 if(key==='route'){
  const target=$('target').value,reason=$('reason').value.trim(),v=validateEscalation(c,target,reason);
  if(!v.ok){notice(v.errors.join(' '));return}
  c.routing={target,reason,priority:v.priority,at:nowIso(),evidence:c.note,diagnostic:c.diagnostics.at(-1)||null};c.state='Escalated';
  await change(c,'Specialist escalation recorded',target+': '+reason.slice(0,210));return
 }
 if(key==='close'){
  const g=canClose(c);if(!g.ok){notice(g.problems.join(' '));return}
  c.state='Resolved';await change(c,'Case closed with verification','Passing test, investigation notes and human-approved update recorded.');return;
 }
 if(key==='reopen'){c.state='Investigating';c.verified=false;await change(c,'Case reopened','Prior resolution cannot be assumed; re-test required.');return}
 if(key==='publish'){
  const g=canClose(c),title=$('article-name').value.trim(),steps=$('article-steps').value.split('\n').map(x=>x.trim()).filter(Boolean);
  if(!g.ok){notice('Article blocked: '+g.problems.join(' '));return}
  if(title.length<12||steps.length<3||steps.some(x=>x.length<12)){notice('Add a clear title and at least three actionable steps.');return}
  const id='KB-'+String(state.articles.length+1).padStart(3,'0');state.articles.push({id,title,steps,kind:c.kind,approved:true,from:c.id+' verified fictional case',scope:'Independent simulation only.'});
  await change(c,'Knowledge article published',id+' / '+title);return;
 }
 if(key==='eval'){
  const results=evaluateBaseline(),pass=results.filter(x=>x.pass).length;
  $('eval-output').innerHTML='<div class="notice success">'+pass+'/'+results.length+' deterministic cases matched the reference categories. NOT an LLM evaluation.<br>'+results.map(x=>esc(x.label)+' → '+esc(x.received)).join('<br>')+'</div>';return
 }
 if(key==='ai'){
  const draft=$('reply').value.trim();if(draft.length<30){notice('Write a response before requesting critique.');return}
  try{
   const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:c.kind,caseId:c.id,draft,observations:c.note.slice(0,800),label:diagnostic(c).label})});
   const v=await r.json();if(!r.ok)throw Error(v.error||'Provider unavailable');
   state.aiRuns.push({id:c.id,at:nowIso(),output:v});await change(c,'External model critique recorded',v.model+' / no automatic action performed.');
  }catch(e){notice('Live AI unavailable: '+e.message+'. No simulated text is presented as actual model output.');}return
 }
}
async function start(){
 try{db=await openDB();const previous=await read();if(previous?.cases?.length===4){state=previous;state.version=MODEL_VERSION;await save();}else await save()}catch(e){console.warn('Browser persistence unavailable',e);db=null;}
 function enter(){ $('landing').hidden=true;$('desk').hidden=false;history.replaceState({},'','?desk=1');scrollTo(0,0);render()}
 function home(){ $('desk').hidden=true;$('landing').hidden=false;history.replaceState({},'','/');scrollTo(0,0)}
 $('begin').onclick=enter;$('enter-desk').onclick=enter;$('nav-desk').onclick=e=>{e.preventDefault();enter()};$('back-home').onclick=home;
 $('reset-data').onclick=async()=>{if(!confirm('Reset your local fictional casebook?'))return;state=fresh();chosen='CW-204';tab='investigate';feedback='';await save();render()};
 $('case-list').onclick=e=>{const b=e.target.closest('[data-case]');if(!b)return;chosen=b.dataset.case;tab='investigate';feedback='';render()};
 document.querySelector('.case-tabs').onclick=e=>{const b=e.target.closest('[data-tab]');if(!b)return;tab=b.dataset.tab;feedback='';render()};
 $('tab-panel').onclick=e=>{const b=e.target.closest('[data-action]');if(b)action(b.dataset.action)};
 try{const r=await fetch('/api/status');const j=await r.json();aiEnabled=!!j.configured;$('ai-status').textContent=aiEnabled?'Model configured: available for review only.':'No model key configured; AI requests disabled.'}catch(e){$('ai-status').textContent='Model connector status unavailable.'}
 if(location.search.includes('desk=1'))enter();
}
start();