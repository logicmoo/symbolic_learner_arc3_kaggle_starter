export function replaceWorkbenchLocation(url:URL,label:string){
  window.history.replaceState(null,"",`${url.pathname}${url.search}${url.hash}`);
  window.dispatchEvent(new CustomEvent("workbench:navigation",{detail:{label}}));
}
