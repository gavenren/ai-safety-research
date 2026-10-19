// Fixed rules for the prospective live case series. No reference target is input.
export function decide(rule, current, later) {
  if (!Number.isInteger(current.x) || ![0,1].includes(current.y)) throw new Error('Invalid observed fields');
  if (!Array.isArray(later) || later.some(c => !['add1','sub1','set0','set1','flip_y'].includes(c))) throw new Error('Invalid verified log');
  const x=current.x, y=current.y;
  if (rule==='full_restore') return {status:'complete', x:0, y:0};
  if (rule==='field_restore') return {status:'complete', x:0, y};
  if (rule==='subtract') return {status:'complete', x:x-1, y};
  if (rule==='value_guard') return x===1 ? {status:'complete',x:0,y} : {status:'abstain',x,y};
  if (rule==='log_revision_guard') return later.every(c=>c==='flip_y') ? {status:'complete',x:0,y} : {status:'abstain',x,y};
  if (rule==='log_provenance') return {status:'complete',x:later.some(c=>c.startsWith('set'))?x:x-1,y};
  throw new Error('Unknown rule');
}
