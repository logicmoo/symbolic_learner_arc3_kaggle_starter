from __future__ import annotations

import base64, copy, hashlib, json, os, re, shutil, subprocess, tempfile, urllib.request
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

from PIL import Image, ImageDraw
from llm_providers import LlmConfigurationError
from llm_workflows import LlmWorkflowEngine, TransactionDefinition, WorkflowAwareLlmProviderRouter
from project_paths import prompts_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OPERATION_PATH = ROOT / "config" / "workflow_operations.json"
DEFAULT_DATATYPE_PATH = ROOT / "config" / "workflow_datatypes.json"

def txt(v: Any) -> str: return str(v or "").strip()
def read_obj(p: Path) -> dict[str, Any]:
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise LlmConfigurationError(f"Expected JSON object: {p}")
    return v
def slug(s:str)->str:return re.sub(r"[^A-Za-z0-9_]+","_",s).strip("_").lower()

@dataclass(frozen=True)
class Impl:
    id:str; label:str; species:str; handler:str|None=None; transaction:str|None=None; runner_method:str|None=None
@dataclass(frozen=True)
class Operation:
    id:str; label:str; description:str; inputs:dict[str,str]; outputs:dict[str,str]; implementations:tuple[Impl,...]
    def impl(self, wanted:str|None)->Impl:
        if wanted:
            for x in self.implementations:
                if x.id==wanted:return x
            raise LlmConfigurationError(f"Operation {self.id!r} has no implementation {wanted!r}")
        return self.implementations[0]
@dataclass
class Slot:
    datatype:str; value:Any; producer:str
    def json(self):
        v=self.value
        if isinstance(v,Path):v=str(v)
        elif isinstance(v,list):v=[str(x) if isinstance(x,Path) else x for x in v]
        return {"datatype":self.datatype,"producer":self.producer,"value":v}

def load_operations(path:Path=DEFAULT_OPERATION_PATH)->tuple[Operation,...]:
    rows=[]
    for r in read_obj(path).get("operations",[]):
        imps=[]
        for i in r.get("implementations",[]):
            species=txt(i.get("species"))
            if species not in {"python","llm","prolog"}: raise LlmConfigurationError(f"Bad species {species!r}")
            imps.append(Impl(txt(i["id"]),txt(i.get("label")) or txt(i["id"]),species,txt(i.get("handler")) or None,txt(i.get("transaction")) or None,txt(i.get("runner_method")) or None))
        rows.append(Operation(txt(r["id"]),txt(r.get("label")) or txt(r["id"]),txt(r.get("description")),dict(r.get("inputs") or {}),dict(r.get("outputs") or {}),tuple(imps)))
    return tuple(rows)

def expand_subworkflows(workflows):
    """Expand reusable workflow calls while preserving typed slot bindings."""
    registry={txt(w.get("id")):w for w in workflows if isinstance(w,Mapping) and txt(w.get("id"))}
    def expand(workflow,prefix="",bindings=None,stack=()):
        wid=txt(workflow.get("id"))
        if wid in stack:raise LlmConfigurationError("Subworkflow cycle: "+" -> ".join((*stack,wid)))
        bindings=dict(bindings or {})
        def slot(name):
            name=txt(name)
            return bindings.get(name,name if not prefix else f"{prefix}__{name}")
        out=[]
        for n,raw_step in enumerate(workflow.get("steps") or [],1):
            if not isinstance(raw_step,Mapping):continue
            step=copy.deepcopy(raw_step);sid=txt(step.get("id")) or f"step_{n}"
            if step.get("subworkflow"):
                target_id=txt(step.get("subworkflow"));target=registry.get(target_id)
                if target is None:raise LlmConfigurationError(f"Workflow {wid!r} references unknown subworkflow {target_id!r}")
                target_inputs=dict(target.get("input_slots") or {});target_outputs=dict(target.get("output_slots") or {})
                call_inputs=dict(step.get("inputs") or {});call_outputs=dict(step.get("outputs") or {})
                missing=set(target_inputs)-set(call_inputs);unknown_in=set(call_inputs)-set(target_inputs);unknown_out=set(call_outputs)-set(target_outputs)
                if missing or unknown_in or unknown_out:raise LlmConfigurationError(f"Subworkflow {target_id!r} port mismatch missing={sorted(missing)} unknown_inputs={sorted(unknown_in)} unknown_outputs={sorted(unknown_out)}")
                nested={txt(internal):slot(external) for port,internal in target_inputs.items() for external in [call_inputs[port]]}
                nested.update({txt(target_outputs[port]):slot(external) for port,external in call_outputs.items()})
                call_prefix=f"{prefix}__{sid}" if prefix else sid
                out.extend(expand(target,call_prefix,nested,(*stack,wid)))
                continue
            step["id"]=f"{prefix}__{sid}" if prefix else sid
            step["inputs"]={port:slot(value) for port,value in (step.get("inputs") or {}).items()}
            step["outputs"]={port:slot(value) for port,value in (step.get("outputs") or {}).items()}
            out.append(step)
        return out
    cooked=[]
    for workflow in workflows:
        if not isinstance(workflow,Mapping):continue
        row=copy.deepcopy(workflow);row["steps"]=expand(row)
        repeat=dict(row.get("repeat") or {});start=txt(repeat.get("from"))
        if start:
            match=next((step["id"] for step in row["steps"] if step.get("id")==start or txt(step.get("id")).startswith(start+"__")),None)
            if match is None:raise LlmConfigurationError(f"Workflow {row.get('id')!r} repeat starts at unknown step {start!r}")
            repeat["from"]=match;row["repeat"]=repeat
        cooked.append(row)
    return cooked

class OperationAwareWorkflowRouter(WorkflowAwareLlmProviderRouter):
    def __init__(self,config_path,*,workflow_path=None,operation_path=None,datatype_path=None,**kw):
        self.operation_path=Path(operation_path or os.getenv("WORLD_WORKBENCH_OPERATION_CONFIG") or os.getenv("ARC3_WORKFLOW_OPERATION_CONFIG") or DEFAULT_OPERATION_PATH).resolve()
        self.datatype_path=Path(datatype_path or os.getenv("WORLD_WORKBENCH_DATATYPE_CONFIG") or os.getenv("ARC3_WORKFLOW_DATATYPE_CONFIG") or DEFAULT_DATATYPE_PATH).resolve()
        self.datatypes=tuple(read_obj(self.datatype_path).get("types",[]))
        self.datatype_by_id={txt(x["id"]):x for x in self.datatypes}
        self.operations=load_operations(self.operation_path); self.operation_by_id={x.id:x for x in self.operations}
        for t in self.operations:
            for d in (*t.inputs.values(),*t.outputs.values()):
                if d not in self.datatype_by_id: raise LlmConfigurationError(f"Operation {t.id!r} references unknown datatype {d!r}")
        real=Path(workflow_path or os.getenv("WORLD_WORKBENCH_WORKFLOW_CONFIG") or os.getenv("ARC3_LLM_WORKFLOW_CONFIG") or ROOT/"config"/"llm_workflows.json").resolve()
        raw=read_obj(real); cooked=copy.deepcopy(raw); cooked["llm_workflows"]=expand_subworkflows(cooked.get("llm_workflows") or []); synthetic=[]; self.operation_step_by_transaction_id={}
        for wf in cooked.get("llm_workflows",[]):
            wid=txt(wf.get("id")) or "workflow"; out=[]
            for n,step in enumerate(wf.get("steps",[]),1):
                if not isinstance(step,dict) or not step.get("operation"): out.append(step); continue
                tid=txt(step["operation"])
                if tid not in self.operation_by_id: raise LlmConfigurationError(f"Unknown operation {tid!r}")
                operation=self.operation_by_id[tid]; operation.impl(txt(step.get("implementation")) or None)
                badin=set((step.get("inputs") or {}))-set(operation.inputs); badout=set((step.get("outputs") or {}))-set(operation.outputs)
                if badin or badout: raise LlmConfigurationError(f"Unknown operation ports inputs={sorted(badin)} outputs={sorted(badout)}")
                sid=f"__operation__{slug(wid)}__{slug(txt(step.get('id')) or str(n))}"
                synthetic.append({"id":sid,"label":operation.label,"kind":"runner_method","runner_method":"__typed_operation__","requires_vision":False,"combine_safe":False})
                self.operation_step_by_transaction_id[sid]=copy.deepcopy(step)
                out.append({"id":txt(step.get("id")) or f"step_{n}","transaction":sid,"continue_on_error":bool(step.get("continue_on_error"))})
            wf["steps"]=out
        cooked.setdefault("llm_transactions",[]).extend(synthetic)
        fd,name=tempfile.mkstemp(prefix="arc3_operations_",suffix=".json");os.close(fd);self._operation_workflow_path=Path(name)
        self._operation_workflow_path.write_text(json.dumps(cooked),encoding="utf-8")
        super().__init__(config_path,workflow_path=self._operation_workflow_path,**kw)
        self.workflow_path=real
        for t in self.operations:
            for i in t.implementations:
                if i.species=="llm" and i.transaction not in self.transaction_by_id: raise LlmConfigurationError(f"Unknown operation transaction {i.transaction!r}")
    def __del__(self):
        try: super().__del__()
        finally:
            try:self._operation_workflow_path.unlink(missing_ok=True)
            except Exception:pass

def node_root(engine):
    store,node=engine.runner._require_node(); root=node.path/"workflow_data";root.mkdir(exist_ok=True)
    return store,node,root
def paths(v):
    if isinstance(v,Slot):v=v.value
    if v is None:return []
    if isinstance(v,(str,Path)):return [Path(v)]
    if isinstance(v,Mapping):
        if "path" in v:return [Path(str(v["path"]))]
        if "images" in v:return paths(v["images"])
    if isinstance(v,list):
        out=[]
        for x in v:out+=paths(x)
        return out
    return []
def manifest(ps,source,dest):
    rows=[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"index":i} for i,p in enumerate(ps)]
    data={"source":source,"images":rows,"created_at":datetime.now(timezone.utc).isoformat()}
    dest.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8");return data
def copy_images(ps,dest,prefix):
    dest.mkdir(parents=True,exist_ok=True);out=[]
    for i,p in enumerate(ps,1):
        if not p.exists():continue
        q=dest/f"{prefix}_{i:03d}{p.suffix.lower() or '.png'}";shutil.copy2(p,q);out.append(q)
    return out

def grab_arc3_state(e,inp,par):
    s,n,r=node_root(e);p=s.parent_node(n);src=([p.image_path] if p else [])+[n.image_path];out=copy_images(src,r/"source_arc3","arc3")
    return {"images":out,"manifest":manifest(out,"arc3_state",r/"source_arc3_manifest.json")}
def disk_directory(e,inp,par):
    d=Path(txt(par.get("directory")) or os.getenv("WORLD_WORKBENCH_IMAGE_DIR","") or os.getenv("ARC3_WORKFLOW_IMAGE_DIR","") or input("Image directory: ")).expanduser().resolve()
    src=sorted(x for x in d.iterdir() if x.suffix.lower() in {".png",".jpg",".jpeg",".webp",".gif",".bmp"});_,_,r=node_root(e);out=copy_images(src,r/"source_disk","disk")
    if not out:raise RuntimeError(f"No images in {d}")
    return {"images":out,"manifest":manifest(out,f"disk:{d}",r/"source_disk_manifest.json")}
def ask_upload(e,inp,par):
    try:
        from tkinter import Tk,filedialog
        w=Tk();w.withdraw();src=[Path(x) for x in filedialog.askopenfilenames(title="Choose workflow images")];w.destroy()
    except Exception:src=[Path(x.strip()) for x in input("Image paths (; separated): ").split(";") if x.strip()]
    _,_,r=node_root(e);out=copy_images(src,r/"source_upload","upload")
    if not out:raise RuntimeError("No images selected")
    return {"images":out,"manifest":manifest(out,"user_upload",r/"source_upload_manifest.json")}
def generated(e,inp,par):
    _,_,r=node_root(e);d=r/"source_generated";d.mkdir(exist_ok=True);out=[]
    for k in range(2):
        im=Image.new("RGB",(64,64),"black");dr=ImageDraw.Draw(im);dr.rectangle((8+k*6,8,23+k*6,23),fill="red");dr.rectangle((35,34-k*4,47,47-k*4),outline="yellow",width=2)
        p=d/f"generated_{k}.png";im.save(p);out.append(p)
    return {"images":out,"manifest":manifest(out,"generated",r/"source_generated_manifest.json")}
def select_arc3_world(e,inp,par):
    game_id=txt(par.get("game_id")) or "ls20";runner=e.runner
    if txt(getattr(runner,"game_id",""))!=game_id:runner.switch_game(game_id)
    else:runner.restart_game()
    return {"world":{"adapter":"arc3","environment_id":game_id,"episode":int(getattr(runner,"detected_level",1))}}
def await_human_arc3_action(e,inp,par):
    runner=e.runner
    print("Human demonstration: choose an ARC3 action")
    for row in runner.action_table():print(f"  {row['index']}: {row['name']}"+(" (x,y)" if row.get("complex") else ""))
    choice=txt(par.get("action")) or input("Action index or name: ").strip()
    action=runner.resolve_action(int(choice) if choice.isdigit() else choice);data=dict(par.get("data") or {})
    complex_check=getattr(action,"is_complex",None)
    if callable(complex_check) and complex_check() and not {"x","y"}.issubset(data):
        data["x"]=int(input("x: "));data["y"]=int(input("y: "))
    before=str(getattr(getattr(runner,"current_node",None),"path",""));runner.step(action,data=data);after=str(getattr(getattr(runner,"current_node",None),"path",""))
    return {"intervention":{"actor":"human","action":getattr(action,"name",str(action)),"data":data,"before_node":before,"after_node":after}}
def continue_human_observation(e,inp,par):
    configured=par.get("continue")
    if configured is None:configured=input("Observe another human action? [Y/n]: ").strip().lower() not in {"n","no","q","quit"}
    return {"continue":bool(configured)}
def advance_observation(e,inp,par):return {"current":inp.get("next")}
def remote_url(e,inp,par):
    u=txt(par.get("url")) or os.getenv("WORLD_WORKBENCH_IMAGE_URL","") or os.getenv("ARC3_WORKFLOW_IMAGE_URL","") or input("Image URL: ");_,_,r=node_root(e);d=r/"source_url";d.mkdir(exist_ok=True);raw=d/"download"
    raw.write_bytes(urllib.request.urlopen(u,timeout=30).read())
    with Image.open(raw) as im:p=d/"remote.png";im.convert("RGBA").save(p)
    raw.unlink(missing_ok=True);return {"images":[p],"manifest":manifest([p],u,r/"source_url_manifest.json")}
def clipboard(e,inp,par):
    from PIL import ImageGrab
    im=ImageGrab.grabclipboard()
    if not isinstance(im,Image.Image):raise RuntimeError("Clipboard has no image")
    _,_,r=node_root(e);p=r/"clipboard.png";im.save(p);return {"images":[p],"manifest":manifest([p],"clipboard",r/"clipboard_manifest.json")}
def video_frames(e,inp,par):
    src=Path(txt(par.get("path")) or os.getenv("WORLD_WORKBENCH_VIDEO","") or os.getenv("ARC3_WORKFLOW_VIDEO","") or input("Video path: ")).resolve();_,_,r=node_root(e);d=r/"video_frames";d.mkdir(exist_ok=True)
    if src.suffix.lower()==".gif":
        out=[];im=Image.open(src);i=0
        while True:
            try:im.seek(i)
            except EOFError:break
            p=d/f"frame_{i:04d}.png";im.convert("RGBA").save(p);out.append(p);i+=1
    else:
        if not shutil.which("ffmpeg"):raise RuntimeError("ffmpeg required")
        subprocess.run(["ffmpeg","-y","-i",str(src),"-vf",f"fps={float(par.get('fps',1)):g}",str(d/"frame_%04d.png")],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);out=sorted(d.glob("frame_*.png"))
    return {"images":out,"manifest":manifest(out,f"video:{src}",r/"video_manifest.json")}
def camera(e,inp,par):
    try:import cv2
    except ImportError as x:raise RuntimeError("opencv-python required") from x
    c=cv2.VideoCapture(int(par.get("camera_index",0)));ok,frame=c.read();c.release()
    if not ok:raise RuntimeError("Camera capture failed")
    _,_,r=node_root(e);p=r/"camera.png";cv2.imwrite(str(p),frame);return {"images":[p],"manifest":manifest([p],"camera",r/"camera_manifest.json")}
def normalize(e,inp,par):
    _,_,r=node_root(e);d=r/"normalized";d.mkdir(exist_ok=True);out=[]
    for i,p in enumerate(paths(inp.get("images")),1):
        with Image.open(p) as im:q=d/f"normalized_{i:03d}.png";im.convert("RGBA").save(q);out.append(q)
    if not out:raise RuntimeError("No images to normalize")
    return {"images":out,"manifest":manifest(out,"normalized",r/"normalized_manifest.json")}
def sync_objects(e,inp,par):
    s,n,r=node_root(e);data={"semantic_type":"individual_object","objects":[{"id":k,"identity_fact":v,"representations":["image_region","turtle_program","object_properties"]} for k,v in sorted(s.registry_identities().items())],"images":[str(x) for x in paths(inp.get("images"))],"object_properties":str(n.path/"objects.pl"),"turtle_programs":[str(x) for x in (n.path/"turtle_from_image.pl",n.path/"turtle_from_diff.pl") if x.exists()]}
    p=r/"object_manifest.json";p.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8");return {"object_manifest":p}
def render_turtle(e,inp,par):
    _,n,r=node_root(e);src=paths(inp.get("turtle")) or [n.path/"turtle_from_image.pl"];d=r/"turtle_renders";d.mkdir(exist_ok=True);out=[]
    pat=re.compile(r"turtle_program\(\s*([A-Za-z0-9_]+)\s*,\s*\[(.*?)\]\s*\)\s*\.",re.S)
    for f in src:
        if not f.exists():continue
        text=f.read_text(encoding="utf-8")
        programs=pat.findall(text) or [("scene",text)]
        for name,body in programs:
            im=Image.new("RGB",(512,512),"black");dr=ImageDraw.Draw(im);x=y=0;direction=0;pen=False;color="white";width=1
            for cmd in re.split(r",\s*(?![^()]*\))",body):
                cmd=cmd.strip()
                if cmd=="penup":pen=False
                elif cmd=="pendown":pen=True
                elif m:=re.match(r"set_pos\((-?\d+),\s*(-?\d+)\)",cmd):x,y=map(int,m.groups())
                elif m:=re.match(r"setcolor\('?(\w+)'?\)",cmd):color=m.group(1)
                elif m:=re.match(r"pen_width\((\d+)\)",cmd):width=int(m.group(1))
                elif m:=re.match(r"rot\((-?\d+)\)",cmd):direction=(direction+round(int(m.group(1))/90))%4
                elif m:=re.match(r"fwd\((\d+)\)",cmd):
                    dx,dy=((1,0),(0,1),(-1,0),(0,-1))[direction]
                    for _ in range(int(m.group(1))):
                        x+=dx;y+=dy
                        if pen:dr.rectangle((x*8,y*8,(x+width)*8-1,(y+width)*8-1),fill=color)
            p=d/f"{slug(name) or 'scene'}.png";im.save(p);out.append(p)
    if not out:raise RuntimeError("No Turtle programs rendered")
    mp=r/"turtle_render_manifest.json";mp.write_text(json.dumps({"images":[str(x) for x in out]},indent=2)+"\n",encoding="utf-8");return {"images":out,"render_manifest":mp}
def display(e,inp,par):
    ps=paths(inp.get("images"));_,_,r=node_root(e)
    if not ps:raise RuntimeError("No images to display")
    opened=[]
    if (os.getenv("WORLD_WORKBENCH_SHOW_IMAGES") or os.getenv("ARC3_WORKFLOW_SHOW_IMAGES","1")) not in {"0","false"}:
        for p in ps:
            try:os.startfile(p) if os.name=="nt" else Image.open(p).show();opened.append(str(p))
            except Exception:pass
    data={"images":[str(x) for x in ps],"opened":opened};(r/"display_session.json").write_text(json.dumps(data,indent=2)+"\n");return {"display_session":data}
def validate(e,inp,par):
    s,n,r=node_root(e);files=[s.object_registry_path]+[n.path/x for x in ("objects.pl","differences.pl","similarities.pl","turtle_from_image.pl","turtle_from_diff.pl","rules.pl")]
    data={"valid":all(x.exists() for x in files[:2]),"checks":[{"path":str(x),"exists":x.exists(),"nonempty":x.exists() and x.stat().st_size>0} for x in files]}
    p=r/"validation_report.json";p.write_text(json.dumps(data,indent=2)+"\n");a=r/"validation_audit.md";a.write_text("# Artifact validation\n\n"+json.dumps(data,indent=2)+"\n");return {"validation":data,"audit":a}
def report(e,inp,par):
    _,n,r=node_root(e);p=r/"workflow_report.md";p.write_text("# Typed workflow report\n\n"+"".join(f"- `{k}`: `{v.datatype}` from `{v.producer}`\n" for k,v in sorted(e._workflow_slots.items())));return {"report":p}

HANDLERS={"select_arc3_world":select_arc3_world,"await_human_arc3_action":await_human_arc3_action,"continue_human_observation":continue_human_observation,"advance_observation":advance_observation,"grab_arc3_state":grab_arc3_state,"video_to_frames":video_frames,"ask_user_to_upload":ask_upload,"images_from_disk_directory":disk_directory,"clipboard_image":clipboard,"remote_image_url":remote_url,"camera_capture":camera,"generated_test_pattern":generated,"normalize_images":normalize,"synchronize_object_representations":sync_objects,"render_turtle_artifacts":render_turtle,"display_images":display,"validate_artifact_bundle":validate,"publish_workflow_report":report}

def seed(e):
    s,n,_=node_root(e);p=s.parent_node(n);e._workflow_slots={"arc3_state":Slot("arc3_state",{"current_image":str(n.image_path),"parent_image":str(p.image_path) if p else None},"workflow"),"artifact_bundle":Slot("artifact_bundle",{"node":str(n.path),"registry":str(s.object_registry_path)},"workflow")}
def save_slots(e):
    _,_,r=node_root(e);(r/"slot_manifest.json").write_text(json.dumps({"slots":{k:v.json() for k,v in e._workflow_slots.items()}},indent=2,default=str)+"\n")
def resolve_inputs(e,t,c):
    m=dict(c.get("inputs") or {});return {p:(e._workflow_slots[m[p]].value if p in m and m[p] in e._workflow_slots else dict(c.get("parameters") or {}) if p=="request" else None) for p in t.inputs}
def store_outputs(e,t,c,vals):
    m=dict(c.get("outputs") or {})
    for p,d in t.outputs.items():
        if p in vals:e._workflow_slots[txt(m.get(p)) or f"{c.get('id')}_{p}"]=Slot(d,vals[p],txt(c.get("id")) or t.id)
    save_slots(e)
def artifact_outputs(e,t):
    s,n,r=node_root(e);out={}
    for p,d in t.outputs.items():
        out[p]={"object_collection":n.path/"objects.pl","turtle_program_file":n.path/"turtle_from_image.pl","transition_evidence":n.path/"differences.pl","rule_set":n.path/"rules.pl","audit_report":n.path/"artifact_audit.md","validation_report":r/"validation_report.json","artifact_bundle":{"node":str(n.path),"registry":str(s.object_registry_path)}}.get(d)
        if d=="object_manifest":out[p]=sync_objects(e,{},{}).get("object_manifest")
    return {k:v for k,v in out.items() if v is not None}

def execute_operation(e,tx):
    r=e.router;c=r.operation_step_by_transaction_id[tx.transaction_id];t=r.operation_by_id[txt(c["operation"])];i=t.impl(txt(c.get("implementation")) or None);inp=resolve_inputs(e,t,c);par=dict(c.get("parameters") or {})
    print(f"Operation {t.label}: {i.label} [{i.species}]")
    if i.species=="python":vals=HANDLERS[i.handler](e,inp,par)
    elif i.species=="prolog":
        m=getattr(e.runner,i.runner_method,None)
        if not callable(m):raise RuntimeError(f"Missing runner method {i.runner_method}")
        m();vals=artifact_outputs(e,t)
    else:
        target=r.transaction_by_id[i.transaction];step=SimpleNamespace(profile_id=txt(c.get("profile")) or None,model_id=txt(c.get("model")) or None,analysis_level=int(c["analysis_level"]) if c.get("analysis_level") else None);profile=e._resolve_profile(step,target)
        e._active_operation_images=[p for v in inp.values() for p in paths(v) if p.exists()]
        try:
            target=replace(target,include_parent_image=False,include_current_image=False) if e._active_operation_images else target
            {"full_analysis":e._run_full_analysis,"llm_artifacts":e._run_artifact_transaction,"llm_text":e._run_text_transaction}[target.kind](target,profile)
        finally:e._active_operation_images=[]
        vals=artifact_outputs(e,t)
    store_outputs(e,t,c,vals)

def install_operation_workflows():
    from multillm_runner import MultiLlmArc3Runner
    if getattr(MultiLlmArc3Runner,"_arc3_typed_operations_installed",False):return
    def router(self):
        if not isinstance(self._llm_router,OperationAwareWorkflowRouter):self._llm_router=OperationAwareWorkflowRouter(prompts_path())
        return self._llm_router
    def reload(self,*,active_model_id=None):
        self._llm_router=OperationAwareWorkflowRouter(prompts_path());self._gpt_analyzer=None
        if active_model_id:
            try:self._llm_router.select_model(active_model_id)
            except Exception:pass
        return self._llm_router
    MultiLlmArc3Runner.llm_router=router;MultiLlmArc3Runner.reload_llm_router=reload;MultiLlmArc3Runner._arc3_typed_operations_installed=True
    oldrun=LlmWorkflowEngine.run
    def run(e,w):seed(e);oldrun(e,w);save_slots(e)
    run._arc3_typed_operations=True;LlmWorkflowEngine.run=run
    oldrm=LlmWorkflowEngine._run_runner_method
    def rm(e,tx):
        if isinstance(e.router,OperationAwareWorkflowRouter) and tx.transaction_id in e.router.operation_step_by_transaction_id:return execute_operation(e,tx)
        return oldrm(e,tx)
    LlmWorkflowEngine._run_runner_method=rm
    oldreq=LlmWorkflowEngine._request_content
    def req(e,*a,**k):
        c=oldreq(e,*a,**k);ps=getattr(e,"_active_operation_images",[])
        if not ps:return c
        c=[x for x in c if x.get("type")!="input_image"]
        for j,p in enumerate(ps,1):c += [{"type":"input_text","text":f"Typed workflow source image {j}:"},{"type":"input_image","image_url":"data:image/png;base64,"+base64.b64encode(p.read_bytes()).decode(),"detail":"high"}]
        return c
    LlmWorkflowEngine._request_content=req
