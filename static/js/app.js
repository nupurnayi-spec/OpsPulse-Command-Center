async function refreshOverview(){
 try{
  const r=await fetch('/api/overview',{cache:'no-store'});
  if(!r.ok)return;
  const d=await r.json();
  const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
  set('avgHealth',`${d.average_asset_health}%`);set('kpiHealth',`${d.average_asset_health}%`);set('kpiCritical',d.critical_assets);set('kpiIncidents',d.open_incidents);set('kpiCpu',`${d.system.cpu}%`);
  const t=document.getElementById('lastUpdate');if(t)t.textContent=`Live • ${d.system.timestamp}`;
  document.documentElement.dataset.lastApiUpdate=d.generated_at;
 }catch(e){console.debug('Telemetry refresh unavailable',e)}
}
refreshOverview();setInterval(refreshOverview,10000);
