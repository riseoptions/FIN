importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
let ready=(async()=>{const py=await loadPyodide();await py.loadPackage(['numpy','pandas','scipy']);const r=await fetch('engine.py');if(!r.ok)throw Error('engine.py laadimine ebaõnnestus');py.runPython(await r.text());return py})();
ready.then(()=>postMessage({ready:true})).catch(e=>postMessage({error:String(e)}));
onmessage=async({data})=>{try{let py=await ready;py.globals.set('request_json',JSON.stringify(data.payload));let result=JSON.parse(py.runPython('bridge(request_json)'));postMessage({id:data.id,result});}catch(e){postMessage({id:data.id,error:String(e)})}};
