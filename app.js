const KEY = "healthTrackerV1";
const $ = id => document.getElementById(id);
const today = () => new Date().toISOString().slice(0,10);
const fmtDate = d => new Date(d + "T12:00:00").toLocaleDateString(undefined,{month:"short",day:"numeric",year:"numeric"});
const state = load();

function load(){
  try { return JSON.parse(localStorage.getItem(KEY)) || {baseline:{},logs:[]}; }
  catch { return {baseline:{},logs:[]}; }
}
function save(){ localStorage.setItem(KEY, JSON.stringify(state)); render(); }
function toast(msg){ const t=$("toast"); t.textContent=msg; t.classList.add("show"); setTimeout(()=>t.classList.remove("show"),2200); }
function bmi(weight,height){ if(!weight || !height) return null; return weight / ((height/100)**2); }
function bmiLabel(v){
  if(v==null) return "—";
  if(v<18.5) return "Underweight";
  if(v<25) return "Healthy range";
  if(v<30) return "Overweight";
  return "Obesity range";
}
function latestWeight(){
  const sorted = [...state.logs].sort((a,b)=>b.date.localeCompare(a.date));
  return sorted.find(x=>x.weight) || (state.baseline.weight ? {weight:state.baseline.weight,date:state.baseline.date}:null);
}
function setView(view){
  document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===view));
  document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
  $("pageTitle").textContent = ({dashboard:"Overview",daily:"Daily Log",baseline:"Baseline",history:"History",settings:"Data"})[view] || "Overview";
  if(view==="history") renderHistory();
  if(view==="dashboard") drawCharts();
}
document.querySelectorAll(".nav-item").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.view)));
document.querySelectorAll("[data-go]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.go)));
document.querySelectorAll("[data-view-target]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.viewTarget)));

$("todayLabel").textContent = new Date().toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric"});
$("logDate").value=today();
$("baselineDate").value=today();

function fillBaseline(){
  const b=state.baseline||{};
  ["baselineDate","age","height","weight","bmi","calorieTarget"].forEach(k=>{
    const key=k==="baselineDate"?"date":k;
    if($(k) && b[key] != null) $(k).value=b[key];
  });
  updateBMI();
}
$("baselineForm").addEventListener("submit",e=>{
  e.preventDefault();
  const height=+$("height").value||0, weight=+$("weight").value||0;
  const calc=bmi(weight,height);
  state.baseline={
    date:$("baselineDate").value||today(),
    age:+$("age").value||null,
    height:height||null,
    weight:weight||null,
    bmi:+$("bmi").value||calc||null,
    calorieTarget:+$("calorieTarget").value||null
  };
  save(); toast("Baseline saved.");
});
function updateBMI(){
  const v=bmi(+$("weight").value, +$("height").value);
  $("bmiPreview").innerHTML = v ? `<strong>${v.toFixed(1)}</strong> ${bmiLabel(v)}` : "Enter height and weight to calculate BMI.";
  if(v && !$("bmi").matches(":focus")) $("bmi").value=v.toFixed(1);
}
$("height").addEventListener("input",updateBMI); $("weight").addEventListener("input",updateBMI);

function fillDaily(date=today()){
  const log=state.logs.find(x=>x.date===date);
  $("logDate").value=date;
  ["calories","exerciseMinutes","activeCalories","steps","dailyWeight","activityType","notes"].forEach(id=>{
    const key={dailyWeight:"weight",activityType:"activity"}[id]||id;
    $(id).value=log?.[key] ?? "";
  });
}
$("logDate").addEventListener("change",e=>fillDaily(e.target.value));
$("dailyForm").addEventListener("submit",e=>{
  e.preventDefault();
  const date=$("logDate").value||today();
  const entry={
    date,
    calories:+$("calories").value||0,
    exerciseMinutes:+$("exerciseMinutes").value||0,
    activeCalories:+$("activeCalories").value||0,
    steps:+$("steps").value||0,
    weight:+$("dailyWeight").value||null,
    activity:$("activityType").value.trim(),
    notes:$("notes").value.trim()
  };
  const i=state.logs.findIndex(x=>x.date===date);
  if(i>=0) state.logs[i]=entry; else state.logs.push(entry);
  state.logs.sort((a,b)=>a.date.localeCompare(b.date));
  save(); toast("Daily log saved.");
});
$("clearDaily").addEventListener("click",()=>fillDaily(today()));

function render(){
  const tlog=state.logs.find(x=>x.date===today())||{};
  const w=latestWeight();
  const currentBMI = w && state.baseline.height ? bmi(w.weight,state.baseline.height) : state.baseline.bmi;
  $("dashCalories").textContent=(tlog.calories||0).toLocaleString();
  $("dashActivity").textContent=(tlog.exerciseMinutes||0).toLocaleString();
  $("dashWeight").textContent=w?.weight ? `${Number(w.weight).toFixed(1)}` : "—";
  $("dashWeightUnit").textContent=w?.weight ? "kg · latest" : "current measurement";
  $("dashBMI").textContent=currentBMI ? Number(currentBMI).toFixed(1) : "—";
  $("dashBMIStatus").textContent=currentBMI ? bmiLabel(currentBMI) : "baseline";
  $("weightChartUnit").textContent="kg";
  renderRecent(); renderHistory(); drawCharts();
}
function renderRecent(){
  const rows=[...state.logs].sort((a,b)=>b.date.localeCompare(a.date)).slice(0,5);
  $("recentActivity").innerHTML=rows.length?rows.map(x=>`
    <div class="activity-row">
      <div class="activity-date">${fmtDate(x.date)}</div>
      <div class="activity-main"><strong>${x.activity||"Daily check-in"}</strong><span>${x.exerciseMinutes||0} min · ${x.steps||0} steps</span></div>
      <div class="activity-cal">${(x.calories||0).toLocaleString()} kcal</div>
    </div>`).join(""):`<div class="empty">No entries yet. Start with today's log.</div>`;
}
function renderHistory(){
  const q=($("historySearch")?.value||"").toLowerCase();
  const rows=[...state.logs].sort((a,b)=>b.date.localeCompare(a.date)).filter(x=>`${x.date} ${x.activity}`.toLowerCase().includes(q));
  $("historyBody").innerHTML=rows.map(x=>`
    <tr>
      <td><strong>${fmtDate(x.date)}</strong></td>
      <td>${(x.calories||0).toLocaleString()}</td>
      <td>${x.exerciseMinutes||0} min</td>
      <td>${x.activeCalories||0}</td>
      <td>${x.weight ? Number(x.weight).toFixed(1)+" kg":"—"}</td>
      <td>${x.activity||"—"}</td>
      <td><div class="row-actions"><button class="icon-btn" data-edit="${x.date}">Edit</button><button class="icon-btn" data-delete="${x.date}">Delete</button></div></td>
    </tr>`).join("");
  $("emptyHistory").style.display=rows.length?"none":"block";
  document.querySelectorAll("[data-edit]").forEach(b=>b.onclick=()=>{fillDaily(b.dataset.edit);setView("daily")});
  document.querySelectorAll("[data-delete]").forEach(b=>b.onclick=()=>{
    if(confirm("Delete this daily entry?")){state.logs=state.logs.filter(x=>x.date!==b.dataset.delete);save();toast("Entry deleted.");}
  });
}
$("historySearch").addEventListener("input",renderHistory);

function drawChart(canvasId, values, labels, unit){
  const c=$(canvasId), ctx=c.getContext("2d"), dpr=window.devicePixelRatio||1;
  const rect=c.getBoundingClientRect(); c.width=rect.width*dpr;c.height=rect.height*dpr;ctx.scale(dpr,dpr);
  const W=rect.width,H=rect.height,pad={l:35,r:12,t:18,b:28};ctx.clearRect(0,0,W,H);
  const max=Math.max(...values,1), min=Math.min(...values,0), range=max-min||1;
  ctx.font="10px DM Sans";ctx.fillStyle="#89958e";ctx.strokeStyle="#e8ece9";ctx.lineWidth=1;
  for(let i=0;i<4;i++){const y=pad.t+(H-pad.t-pad.b)*i/3;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(W-pad.r,y);ctx.stroke();ctx.fillText(Math.round(max-(range*i/3)),4,y+3)}
  const pts=values.map((v,i)=>({x:pad.l+(W-pad.l-pad.r)*(i/(values.length-1||1)),y:pad.t+(H-pad.t-pad.b)*(1-(v-min)/range)}));
  if(pts.length>1){ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.strokeStyle="#2f7658";ctx.lineWidth=2.5;ctx.stroke()}
  pts.forEach((p,i)=>{ctx.beginPath();ctx.arc(p.x,p.y,3.5,0,Math.PI*2);ctx.fillStyle="#2f7658";ctx.fill();ctx.fillStyle="#89958e";ctx.fillText(labels[i],p.x-15,H-8)});
}
function drawCharts(){
  const logs=[...state.logs].sort((a,b)=>a.date.localeCompare(b.date)).slice(-7);
  const labels=logs.map(x=>new Date(x.date+"T12:00:00").toLocaleDateString(undefined,{weekday:"short"}));
  drawChart("calorieChart",logs.length?logs.map(x=>x.calories||0):[0,0,0,0,0,0,0],logs.length?labels:["","","","","","",""],"kcal");
  const wlogs=logs.filter(x=>x.weight);
  drawChart("weightChart",wlogs.length?wlogs.map(x=>+x.weight):[0,0],wlogs.length?wlogs.map(x=>new Date(x.date+"T12:00:00").toLocaleDateString(undefined,{weekday:"short"})):["",""],"kg");
}
$("exportData").addEventListener("click",()=>{
  const blob=new Blob([JSON.stringify(state,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`health-tracker-${today()}.json`;a.click();URL.revokeObjectURL(a.href);
});
$("importData").addEventListener("change",e=>{
  const file=e.target.files[0]; if(!file)return;
  const reader=new FileReader(); reader.onload=()=>{
    try{const data=JSON.parse(reader.result);if(!data.logs||typeof data!=="object")throw Error();
      state.baseline=data.baseline||{};state.logs=Array.isArray(data.logs)?data.logs:[];save();toast("Data imported.");
    }catch{toast("That file is not a valid Health Tracker backup.");}
  }; reader.readAsText(file);
});
$("resetData").addEventListener("click",()=>{
  if(confirm("Clear all Health Tracker data from this browser?")){state.baseline={};state.logs=[];save();fillBaseline();fillDaily();toast("All data cleared.");}
});
window.addEventListener("resize",drawCharts);
fillBaseline();fillDaily();render();
