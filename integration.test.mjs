import assert from 'node:assert/strict';
import {test} from 'node:test';
import graphql from './api/graphql.js';
import lab from './api/lab.js';
import ai from './api/ai.js';
import {fresh,validateEscalation,diagnostic,evaluateBaseline} from './rules.mjs';
async function invoke(handler,method,body){
 const req={method,body},res={statusCode:200,headers:{},setHeader(k,v){this.headers[k.toLowerCase()]=v;return this},status(n){this.statusCode=n;return this},json(value){this.body=value;return this},end(x){this.body=JSON.parse(x);return this}};
 await handler(req,res);return res;
}
test('actual fictional GraphQL endpoint returns HTTP 200 but errors in body',async()=>{
 const r=await invoke(graphql,'POST',{operationName:'UpdateDraftSettings',variables:{settings:{review:true}}});
 assert.equal(r.statusCode,200);assert.equal(r.body.data,null);assert.equal(r.body.simulation,true);
 assert.match(r.body.errors[0].message,/draftId/);
 assert.equal(r.headers['x-casework-simulation'],'true');
});
test('corrected GraphQL request returns success as data',async()=>{
 const r=await invoke(graphql,'POST',{operationName:'UpdateDraftSettings',variables:{draftId:'demo_42',settings:{review:true}}});
 assert.equal(r.statusCode,200);assert.equal(r.body.data.updateDraftSettings.success,true);assert.equal(r.body.errors,undefined);
});
test('fictional API rejects invalid case state',async()=>{const r=await invoke(lab,'POST',{kind:'documents',fault:{stale:'false',security:false}});assert.equal(r.statusCode,422)});
test('legal correctness never gets a technical auto-fix',async()=>{const r=await invoke(lab,'POST',{kind:'legal',fault:{unverified:true}});assert.equal(r.statusCode,200);assert.equal(r.body.pass,false);assert.equal(r.body.label,'UNVERIFIED_REFERENCE')});
test('security incident is urgent and bypasses routine notes',async()=>{
 const c=fresh().cases.find(x=>x.kind==='documents');c.fault.security=true;
 const v=validateEscalation(c,'Security','Possible confidential matter exposure.');
 assert.equal(v.ok,true);assert.equal(v.priority,'Urgent security review');
 assert.equal(validateEscalation(c,'Engineering','Please review the incorrect access.').ok,false);
 const r=await invoke(lab,'POST',{kind:'documents',fault:c.fault});assert.equal(r.body.pass,false);
 assert.equal(r.body.category,'Security');
});
test('standard engineering escalation still needs investigation',()=>{const c=fresh().cases.find(x=>x.kind==='graphql');c.note='Tested GraphQL mutation with missing required variable.';const v=validateEscalation(c,'Engineering','The request returns HTTP 200 with GraphQL errors.');assert.equal(v.ok,false);assert.match(v.errors.join(' '),/diagnostic/i)});
test('AI is fail-closed without explicitly enabled credentials',async()=>{const prev=process.env.CASEWORK_ALLOW_MODEL_CALLS;delete process.env.CASEWORK_ALLOW_MODEL_CALLS;const r=await invoke(ai,'POST',{kind:'login',caseId:'CW-101',draft:'Please help me with the account session issue right away.'});assert.equal(r.statusCode,503);assert.match(r.body.error,/disabled/i);if(prev!==undefined)process.env.CASEWORK_ALLOW_MODEL_CALLS=prev});
test('routing baseline covers four case categories',()=>assert.equal(evaluateBaseline().filter(x=>x.pass).length,8));
