// Bounded, stateless diagnostic server for independent fictional training cases.
// It uses no real customers, identity provider, documents, patents or vendor integration.
export default function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 res.setHeader('X-Casework-Simulation','true');
 if(req.method!=='POST')return res.status(405).json({error:'POST required',simulation:true});
 const b=typeof req.body==='string'?JSON.parse(req.body):req.body||{};
 if(!['login','documents','legal'].includes(b.kind)||typeof b.fault!=='object'||b.fault===null)return res.status(422).json({error:'Invalid fictional scenario',simulation:true});
 const f=b.fault,lines=[];
 let label,pass,category,guidance;
 if(b.kind==='login'){
   if(typeof f.expired!=='boolean')return res.status(422).json({error:'Missing session flag',simulation:true});
   pass=!f.expired;label=pass?'SESSION_VALID':'SESSION_EXPIRED';category='Account/session';
   lines.push('GET /workspace → '+(pass?'200 OK':'401 SESSION_EXPIRED'),'Identity: fictional user validated','Token expiry: '+(pass?'within active session':'earlier than current session'));
   guidance=pass?'The fictional workspace is available.':'Refresh the controlled session; never request a password.';
 } else if(b.kind==='documents'){
   if(typeof f.stale!=='boolean'||typeof f.security!=='boolean')return res.status(422).json({error:'Invalid document flags',simulation:true});
   pass=!f.stale&&!f.security;category=f.security?'Security':'Document state';
   label=f.security?'POSSIBLE_ACCESS_MISMATCH':f.stale?'STALE_SNAPSHOT':'SNAPSHOT_CURRENT';
   lines.push('Source revision: v5','Imported copy: '+(f.stale?'v4':'v5'),'Access review: '+(f.security?'POSSIBLE MISMATCH — STOP':'No unexpected access in fixture'),'No external document service accessed');
   guidance=f.security?'Route urgently to Security; do not perform a routine fix.':f.stale?'Refresh the controlled document snapshot and compare versions.':'Imported version matches source in the fictional exercise.';
 } else {
   pass=false;category='Patent-domain';label='UNVERIFIED_REFERENCE';
   lines.push('Fictional reference P-1842 lacks supporting source','Legal opinion: NOT PERFORMED','Qualified review: REQUIRED');
   guidance='Do not certify patent correctness. Preserve evidence and route to qualified counsel.';
 }
 return res.status(200).json({pass,category,label,lines,guidance,simulation:true,executedOn:'casework-lab-server',timestamp:new Date().toISOString()});
}