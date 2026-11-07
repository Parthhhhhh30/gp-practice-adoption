// Independent fictional GraphQL endpoint. Responds with HTTP 200 and GraphQL-shaped
// application errors, so browser Network inspection is meaningful.
export default function handler(req,res){
 res.setHeader('Cache-Control','no-store');
 res.setHeader('X-Casework-Simulation','true');
 if(req.method!=='POST')return res.status(405).json({errors:[{message:'POST required'}],simulation:true});
 const body=typeof req.body==='string'?JSON.parse(req.body):req.body||{};
 if(body.operationName!=='UpdateDraftSettings')return res.status(400).json({errors:[{message:'Unknown fictional operation'}],simulation:true});
 const v=body.variables||{};
 if(typeof v.draftId!=='string'||!v.draftId.trim())return res.status(200).json({data:null,errors:[{message:'Variable "$draftId" of required type "ID!" was not provided.',extensions:{code:'BAD_USER_INPUT'}}],simulation:true});
 if(v.draftId!=='demo_42')return res.status(200).json({data:null,errors:[{message:'Fictional draft not found.',extensions:{code:'NOT_FOUND'}}],simulation:true});
 return res.status(200).json({data:{updateDraftSettings:{success:true,draftId:v.draftId,review:Boolean(v.settings?.review)}},simulation:true});
}