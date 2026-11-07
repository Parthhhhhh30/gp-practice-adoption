/* Independent CASEWORK simulation. All people, firms, issues and outcomes are fictional. */
export const MODEL_VERSION = 'casework-2.0.2';
export const seeds = [
{id:'CW-101',kind:'login',title:'Access ends after sign-in',firm:'Westbourne IP Chambers',person:'Maya Reed',role:'Associate',channel:'In-app chat',urgency:'Standard',customer:'I can sign in, but the application keeps sending me back to the login page. I need to review a draft this afternoon.',impact:'Attorney cannot reach their workspace.',fault:{expired:true},expected:'Refresh the fictional session and verify successful access.'},
{id:'CW-204',kind:'graphql',title:'The save that never saved',firm:'Oak & Field Legal',person:'Oliver Hart',role:'Patent attorney',channel:'Email',urgency:'High',customer:'I changed the draft settings and clicked Save. The page confirmed it, but when I returned the values were unchanged. Can you investigate?',impact:'Requested changes are not persisted.',fault:{missingId:true},expected:'Inspect the successful HTTP response, find the GraphQL application error, repair the missing ID, and retest.'},
{id:'CW-307',kind:'documents',title:'Document update not appearing',firm:'North Quay Advisory',person:'Isabel Chen',role:'Senior partner',channel:'Slack Connect',urgency:'High',customer:'The source document was updated but the file in our review workspace still shows yesterday’s version. Please confirm what happened.',impact:'Outdated fictional document context may be used in a review.',fault:{stale:true,security:false},expected:'Check source revision versus imported snapshot, refresh the fictional snapshot, and retest. Escalate immediately if a security concern is found.'},
{id:'CW-412',kind:'legal',title:'AI citation needs professional review',firm:'Cedar Bridge Patents',person:'Eleanor Shah',role:'Head of IP',channel:'Email',urgency:'High',customer:'A drafted patent response includes a reference we cannot verify. Is the legal reasoning safe to submit today?',impact:'Potentially unsupported legal material.',fault:{unverified:true},expected:'Do not certify legal correctness. Preserve the questionable reference and route to a qualified patent-domain reviewer.'}
];
export const articles = [
{id:'KB-001',title:'Sign-in loop: verify session state',kind:'login',approved:true,from:'Reviewed simulation fixture',steps:['Confirm the account and affected browser session.','Check whether the simulated access token has expired.','Refresh the session through the supported flow and retest access.','If the loop persists, escalate with a trace identifier and steps to reproduce.'],scope:'Fictional demonstration only; not product-vendor guidance.'},
{id:'KB-002',title:'Successful HTTP request with GraphQL errors',kind:'graphql',approved:true,from:'Reviewed simulation fixture',steps:['Inspect the application response body, not just HTTP status.','Check the GraphQL errors array and variables supplied by the client.','Correct the missing required variable in the simulated test environment.','Retest the mutation and retrieve the updated value.'],scope:'Fictional React/GraphQL environment, not a live service.'}
];
export const nowIso=()=>new Date().toISOString();
export function fresh(){
  return {version:MODEL_VERSION,createdAt:nowIso(),cases:seeds.map(s=>({...structuredClone(s),state:'New',note:'',reply:'',replyApproved:false,fixApplied:false,verified:false,diagnostics:[],routing:null,history:[{at:nowIso(),action:'Case opened',details:'Fictional inbound request created.'}]})),articles:structuredClone(articles),aiRuns:[]};
}
export function diagnostic(c){
 const fault=c.fault||{};
 if(c.kind==='login')return {pass:!fault.expired,category:'Account/session',label:fault.expired?'SESSION_EXPIRED':'SESSION_VALID',lines:['GET /workspace → '+(fault.expired?'401 SESSION_EXPIRED':'200 OK'),'Identity: fictional user account validated','Token expiry: '+(fault.expired?'earlier than current session':'within active session')],guidance:fault.expired?'Refresh the fictional session. Do not ask the customer to share passwords.':'Access succeeds in the simulated session.'};
 if(c.kind==='graphql')return {pass:!fault.missingId,category:'Client/API',label:fault.missingId?'GRAPHQL_VALIDATION_ERROR':'MUTATION_OK',lines:['POST /graphql → HTTP 200','operation: UpdateDraftSettings','variables: '+(fault.missingId?'{settings:{review:true}}':'{draftId:"demo_42",settings:{review:true}}'),fault.missingId?'response.errors[0]: Required variable "draftId" was not provided.':'response.data.updateDraftSettings.success: true'],guidance:fault.missingId?'Correct the missing variable, then retest the persisted value.':'Updated settings retrieved successfully in the fictional service.'};
 if(c.kind==='documents')return {pass:!fault.stale && !fault.security,category:fault.security?'Security':'Document state',label:fault.security?'POSSIBLE_ACCESS_MISMATCH':fault.stale?'STALE_SNAPSHOT':'SNAPSHOT_CURRENT',lines:['Source version: v5','Imported snapshot: '+(fault.stale?'v4':'v5'),'Access review: '+(fault.security?'MISMATCH — STOP ROUTINE INVESTIGATION':'No unexpected access detected'),'Integration: independent simulation; no vendor connection'],guidance:fault.security?'Security-sensitive concern: stop routine debugging and route for urgent specialist review.':fault.stale?'Refresh the fictional imported snapshot and verify the revision.':'Imported version matches the source in this simulation.'};
 return {pass:false,category:'Patent-domain',label:'UNVERIFIED_REFERENCE',lines:['Generated text: reference [P-1842]','Source registry: no supporting entry in fictional evidence set','Legal validation: NOT PERFORMED','Domain reviewer: required'],guidance:'Do not confirm legal accuracy. Ask qualified patent counsel to review the source and reasoning.'};
}
export function validateEscalation(c,target,reason){
 const findings=diagnostic(c),e=[];
 const urgent=Boolean(c.fault?.security)&&target==='Security';
 if(!urgent && (reason||'').trim().length<35)e.push('Provide a specific issue summary (at least 35 characters).');
 if(!urgent && (c.note||'').trim().length<20)e.push('Record investigation evidence (at least 20 characters).');
 // A real potential disclosure must be routed immediately, even if the operator
 // has not yet completed routine documentation. Preserve a short safety summary when available.
 if(c.kind==='legal' && target!=='Patent-domain specialist')e.push('Questionable patent content must go to a qualified patent-domain reviewer.');
 if(c.fault?.security && target!=='Security')e.push('Potential exposure must be routed urgently to Security.');
 if(!c.fault?.security && c.kind!=='legal' && target==='Patent-domain specialist')e.push('Do not route technical access issues for legal correctness review.');
 if(c.kind==='graphql' && target==='Engineering' && !c.diagnostics.length)e.push('Include an executed diagnostic before engineering escalation.');
 if(!urgent && !reason?.trim())e.push('Explain why this route is required.');
 return {ok:e.length===0,errors:e,priority:c.fault?.security?'Urgent security review':c.kind==='legal'?'Qualified-domain review':'Normal specialist review',label:findings.label};
}
export function canClose(c){
 const problems=[];
 if(c.kind==='legal')problems.push('A support specialist cannot certify patent/legal correctness. Specialist review is required.');
 if(c.fault?.security)problems.push('Possible confidentiality incident requires security ownership before routine closure.');
 if(!diagnostic(c).pass)problems.push('A passing diagnostic or verification is required.');
 if(!c.verified)problems.push('Run and record a successful verification.');
 if((c.note||'').trim().length<20)problems.push('Document the investigation evidence (at least 20 characters).');
 if(!c.replyApproved || (c.reply||'').trim().length<45)problems.push('Approve a sufficiently informative customer update.');
 return {ok:problems.length===0,problems};
}
export function checkResponse(text){
 const issues=[];
 if(!text||text.trim().length<45)issues.push('Provide enough context to help the customer (45+ characters).');
 if(/\b(guaranteed|definitely fixed|100% secure|legally correct|approved by the patent office|will be fixed in \d+)/i.test(text||''))issues.push('Remove unsupported guarantees or legal assurances.');
 if(/\b(send (me|us) your password|share your password)\b/i.test(text||''))issues.push('Never request passwords.');
 return issues;
}
export function baseline(c){
 const obs=diagnostic(c);
 const route=c.fault?.security?'Security':c.kind==='legal'?'Patent-domain specialist':c.kind==='graphql'?(c.fault?.missingId?'Engineering':'Customer support'):'Customer support';
 return {route,reason:obs.label,ask:c.kind==='login'?'Which browser and approximate time did the loop occur?':c.kind==='graphql'?'Can you confirm the affected fictional draft and steps?':c.kind==='documents'?'Which source revision do you expect to see?':'Which reference appears unsupported, and can a qualified reviewer inspect the original sources?'};
}
export const evalCases=[
{kind:'login',state:{expired:true},expect:'Customer support',label:'Routine expiry'},
{kind:'login',state:{expired:false},expect:'Customer support',label:'Verified session'},
{kind:'graphql',state:{missingId:true},expect:'Engineering',label:'Reproducible mutation issue'},
{kind:'graphql',state:{missingId:false},expect:'Customer support',label:'Post-fix confirmation'},
{kind:'documents',state:{stale:true,security:false},expect:'Customer support',label:'Stale imported snapshot'},
{kind:'documents',state:{stale:false,security:true},expect:'Security',label:'Unexpected access boundary'},
{kind:'legal',state:{unverified:true},expect:'Patent-domain specialist',label:'Unsupported legal citation'},
{kind:'documents',state:{stale:false,security:false},expect:'Customer support',label:'Current snapshot'}];
export function evaluateBaseline(){return evalCases.map((x,i)=>({id:i+1,label:x.label,expected:x.expect,received:baseline({kind:x.kind,fault:x.state}).route,pass:baseline({kind:x.kind,fault:x.state}).route===x.expect}));}
