from __future__ import annotations

import copy, json, os, subprocess, webbrowser
from pathlib import Path
from typing import Any, Mapping

from llm_workflows import LlmWorkflowEngine, run_workflow_menu
from workflow_tasks import DEFAULT_DATATYPE_PATH, DEFAULT_TASK_PATH, TaskAwareWorkflowRouter

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/"config"/"example_typed_task_workflow.json"
GRAPH=ROOT/"config"/"workflow_datatypes.svg"

def read_obj(p):
    v=json.loads(Path(p).read_text(encoding="utf-8"))
    if not isinstance(v,dict):raise ValueError(f"Expected JSON object: {p}")
    return v
def open_path(p):
    p=Path(p).resolve()
    if os.name=="nt":os.startfile(p)  # type: ignore[attr-defined]
    elif p.suffix.lower() in {".svg",".png",".jpg"}:webbrowser.open(p.as_uri())
    elif os.getenv("EDITOR"):subprocess.run([os.environ["EDITOR"],str(p)],check=False)
    else:print(p.read_text(encoding="utf-8"))
def load_example():return read_obj(EXAMPLE)
def ensure_example(raw):
    rows=raw.setdefault("llm_workflows",[]);ex=load_example()
    if any(isinstance(x,Mapping) and x.get("id")==ex["id"] for x in rows):return False
    rows.append(copy.deepcopy(ex));return True
def validate_write(runner,path,raw):
    old=runner.llm_router();base=Path(old.base_catalog_path);previous=path.read_text(encoding="utf-8")
    path.write_text(json.dumps(raw,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    try:TaskAwareWorkflowRouter(base,workflow_path=path)
    except Exception:path.write_text(previous,encoding="utf-8");raise
    runner.reload_llm_router()

def gui(runner,path,raw):
    import tkinter as tk
    from tkinter import messagebox,simpledialog,ttk
    router=runner.llm_router();ensure_example(raw);workflows=raw["llm_workflows"]
    catalog=read_obj(DEFAULT_TASK_PATH);tasks={x["id"]:x for x in catalog["tasks"]};task_ids=list(tasks);subworkflow_ids=[txt for txt in (str(x.get("id") or "") for x in workflows) if txt]
    datatypes=read_obj(DEFAULT_DATATYPE_PATH)["types"];profiles=sorted(router.profile_by_id);models=["$selected",*sorted(router.model_by_id)]
    root=tk.Tk();root.title("MeTTaFlowWorkbench — Workflow Desktop");root.geometry("1600x900")
    ttk.Label(root,text="Compose typed tasks and reusable subworkflows, then run the selected world-analysis workflow.").pack(anchor="w",padx=10,pady=(10,3))
    tabs=ttk.Notebook(root);tabs.pack(fill="both",expand=True,padx=10)
    wf_tab=ttk.Frame(tabs);task_tab=ttk.Frame(tabs);dt_tab=ttk.Frame(tabs)
    tabs.add(wf_tab,text="Workflows");tabs.add(task_tab,text="Tasks / implementations");tabs.add(dt_tab,text="Datatype manifest")
    wf_tab.columnconfigure(1,weight=1);wf_tab.rowconfigure(0,weight=1)
    left=ttk.Frame(wf_tab);left.grid(row=0,column=0,sticky="ns",padx=(0,8),pady=8)
    wtree=ttk.Treeview(left,columns=("label","steps"),show="headings",height=27);wtree.heading("label",text="Workflow");wtree.heading("steps",text="Steps");wtree.column("label",width=330);wtree.column("steps",width=55);wtree.pack(fill="y",expand=True)
    lbuttons=ttk.Frame(left);lbuttons.pack(fill="x",pady=5)
    right=ttk.Frame(wf_tab);right.grid(row=0,column=1,sticky="nsew",pady=8);right.columnconfigure(1,weight=1);right.rowconfigure(4,weight=1)
    wid=tk.StringVar();label=tk.StringVar()
    ttk.Label(right,text="ID").grid(row=0,column=0,sticky="w");ttk.Entry(right,textvariable=wid).grid(row=0,column=1,sticky="ew",padx=4)
    ttk.Label(right,text="Label").grid(row=1,column=0,sticky="w");ttk.Entry(right,textvariable=label).grid(row=1,column=1,sticky="ew",padx=4)
    ttk.Label(right,text="Description").grid(row=2,column=0,sticky="nw");desc=tk.Text(right,height=4);desc.grid(row=2,column=1,sticky="ew",padx=4)
    ttk.Label(right,text="Ordered items").grid(row=3,column=0,columnspan=2,sticky="w")
    cols=("n","id","type","operation","implementation","inputs","outputs","optional")
    stree=ttk.Treeview(right,columns=cols,show="headings")
    widths=(35,150,75,230,210,260,260,60)
    for c,h,w in zip(cols,("#","Item ID","Type","Task / transaction","Implementation","Input slots","Output slots","Optional"),widths):stree.heading(c,text=h);stree.column(c,width=w)
    stree.grid(row=4,column=0,columnspan=2,sticky="nsew");sbuttons=ttk.Frame(right);sbuttons.grid(row=5,column=0,columnspan=2,sticky="ew",pady=5)
    selected=None;loading=False
    def current():return workflows[selected] if selected is not None and 0<=selected<len(workflows) else None
    def commit():
        if loading or not current():return
        current()["id"]=wid.get().strip();current()["label"]=label.get().strip();current()["description"]=desc.get("1.0","end").strip()
    def refresh_w(select=None):
        wtree.delete(*wtree.get_children())
        for i,w in enumerate(workflows):wtree.insert("","end",iid=str(i),values=(w.get("label") or w.get("id"),len(w.get("steps") or [])))
        if select is not None:wtree.selection_set(str(select));wtree.focus(str(select))
    def summary(s):
        if s.get("subworkflow"):
            ins=", ".join(f"{a}←{b}" for a,b in (s.get("inputs") or {}).items());outs=", ".join(f"{a}→{b}" for a,b in (s.get("outputs") or {}).items())
            return ("subworkflow",s.get("subworkflow",""),"nested workflow",ins,outs)
        if s.get("task"):
            ins=", ".join(f"{a}←{b}" for a,b in (s.get("inputs") or {}).items());outs=", ".join(f"{a}→{b}" for a,b in (s.get("outputs") or {}).items())
            return ("task",s.get("task",""),s.get("implementation",""),ins,outs)
        return ("transaction",s.get("transaction",""),s.get("profile") or s.get("model") or "","", "")
    def refresh_s():
        stree.delete(*stree.get_children())
        for i,s in enumerate((current() or {}).get("steps") or []):typ,op,impl,ins,outs=summary(s);stree.insert("","end",iid=str(i),values=(i+1,s.get("id",""),typ,op,impl,ins,outs,"yes" if s.get("continue_on_error") else ""))
    def load(_=None):
        nonlocal selected,loading
        commit();sel=wtree.selection()
        if not sel:return
        selected=int(sel[0]);w=current();loading=True;wid.set(w.get("id",""));label.set(w.get("label",""));desc.delete("1.0","end");desc.insert("1.0",w.get("description",""));loading=False;refresh_s()
    def add_example():
        ex=load_example();idx=next((i for i,w in enumerate(workflows) if w.get("id")==ex["id"]),None)
        if idx is None:workflows.append(copy.deepcopy(ex));idx=len(workflows)-1
        refresh_w(idx);load()
    def new_workflow():
        workflows.append({"id":f"workflow_{len(workflows)+1}","label":"New typed workflow","description":"","steps":[]});refresh_w(len(workflows)-1);load()
    def delete_workflow():
        nonlocal selected
        if current() and messagebox.askyesno("Delete","Delete selected workflow?"):del workflows[selected];selected=0 if workflows else None;refresh_w(selected);load() if workflows else refresh_s()
    def step_index():
        s=stree.selection();return int(s[0]) if s else None
    def task_dialog(step,title):
        d=tk.Toplevel(root);d.title(title);d.transient(root);d.grab_set();d.columnconfigure(1,weight=1)
        v_id=tk.StringVar(value=step.get("id",""));v_task=tk.StringVar(value=step.get("task",task_ids[0]));v_impl=tk.StringVar(value=step.get("implementation",""));v_profile=tk.StringVar(value=step.get("profile",""));v_model=tk.StringVar(value=step.get("model",""));v_level=tk.StringVar(value=str(step.get("analysis_level","")));v_opt=tk.BooleanVar(value=bool(step.get("continue_on_error")))
        for r,(text,var) in enumerate((("Item ID",v_id),("Task",v_task),("Implementation",v_impl))):ttk.Label(d,text=text).grid(row=r,column=0,sticky="w",padx=6,pady=3);(ttk.Entry(d,textvariable=var) if r==0 else ttk.Combobox(d,textvariable=var,width=50)).grid(row=r,column=1,sticky="ew",padx=6,pady=3)
        task_box=d.grid_slaves(row=1,column=1)[0];task_box.configure(values=task_ids);impl_box=d.grid_slaves(row=2,column=1)[0]
        def update_impl(*_):
            vals=[x["id"] for x in tasks[v_task.get()]["implementations"]];impl_box.configure(values=vals)
            if v_impl.get() not in vals:v_impl.set(vals[0])
        task_box.bind("<<ComboboxSelected>>",update_impl);update_impl()
        texts={}
        for r,(name,key) in enumerate((("Inputs JSON (port → existing slot)","inputs"),("Outputs JSON (port → new slot)","outputs"),("Parameters JSON","parameters")),3):
            ttk.Label(d,text=name).grid(row=r,column=0,sticky="nw",padx=6,pady=3);t=tk.Text(d,height=5,width=65);t.insert("1.0",json.dumps(step.get(key) or {},indent=2));t.grid(row=r,column=1,sticky="ew",padx=6,pady=3);texts[key]=t
        route=ttk.Frame(d);route.grid(row=6,column=0,columnspan=2,sticky="ew",padx=6)
        for c,(name,var,vals) in enumerate((("Profile",v_profile,("",*profiles)),("Model",v_model,("",*models)),("Level",v_level,("","2","3","4")))):ttk.Label(route,text=name).grid(row=0,column=c);ttk.Combobox(route,textvariable=var,values=vals,width=35 if c<2 else 8).grid(row=1,column=c,padx=2)
        ttk.Checkbutton(d,text="Continue on error",variable=v_opt).grid(row=7,column=0,columnspan=2,sticky="w",padx=6)
        ok=False
        def accept():
            nonlocal ok
            try:maps={k:json.loads(t.get("1.0","end") or "{}") for k,t in texts.items()}
            except Exception as e:messagebox.showerror("Invalid JSON",str(e),parent=d);return
            step.clear();step.update({"id":v_id.get().strip(),"task":v_task.get().strip(),"implementation":v_impl.get().strip(),**maps})
            if v_profile.get():step["profile"]=v_profile.get()
            if v_model.get():step["model"]=v_model.get()
            if v_level.get():step["analysis_level"]=int(v_level.get())
            if v_opt.get():step["continue_on_error"]=True
            ok=True;d.destroy()
        b=ttk.Frame(d);b.grid(row=8,column=0,columnspan=2,sticky="ew",padx=6,pady=6);ttk.Button(b,text="OK",command=accept).pack(side="left");ttk.Button(b,text="Cancel",command=d.destroy).pack(side="right");d.wait_window();return ok
    def add_task():
        if not current():return
        s={"id":f"task_{len(current().setdefault('steps',[]))+1}","task":task_ids[0],"implementation":tasks[task_ids[0]]["implementations"][0]["id"],"inputs":{},"outputs":{},"parameters":{}}
        if task_dialog(s,"Add typed task"):current()["steps"].append(s);refresh_s()
    def subworkflow_dialog(step,title):
        available=[x for x in subworkflow_ids if x!=wid.get().strip()]
        chosen=simpledialog.askstring(title,"Subworkflow ID:\n"+"\n".join(available),initialvalue=step.get("subworkflow",available[0] if available else ""),parent=root)
        if not chosen:return False
        try:
            inputs=json.loads(simpledialog.askstring(title,"Input bindings JSON (subworkflow port → current slot)",initialvalue=json.dumps(step.get("inputs") or {},indent=2),parent=root) or "{}")
            outputs=json.loads(simpledialog.askstring(title,"Output bindings JSON (subworkflow port → new slot)",initialvalue=json.dumps(step.get("outputs") or {},indent=2),parent=root) or "{}")
        except Exception as e:messagebox.showerror("Invalid JSON",str(e),parent=root);return False
        step_id=step.get("id") or f"subworkflow_{len(current().setdefault('steps',[]))+1}";step.clear();step.update({"id":step_id,"subworkflow":chosen.strip(),"inputs":inputs,"outputs":outputs});return True
    def add_subworkflow():
        if not current():return
        s={"id":f"subworkflow_{len(current().setdefault('steps',[]))+1}","subworkflow":"","inputs":{},"outputs":{}}
        if subworkflow_dialog(s,"Add subworkflow"):current()["steps"].append(s);refresh_s()
    def edit_task():
        i=step_index()
        if i is None:return
        s=current()["steps"][i]
        if s.get("subworkflow"):
            if subworkflow_dialog(s,"Edit subworkflow"):refresh_s();stree.selection_set(str(i))
            return
        if not s.get("task"):messagebox.showinfo("Legacy transaction","Use Edit Raw JSON for legacy transaction items.");return
        if task_dialog(s,"Edit typed task"):refresh_s();stree.selection_set(str(i))
    def delete_step():
        i=step_index()
        if i is not None:del current()["steps"][i];refresh_s()
    def move(delta):
        i=step_index()
        if i is None:return
        j=i+delta
        if 0<=j<len(current()["steps"]):current()["steps"][i],current()["steps"][j]=current()["steps"][j],current()["steps"][i];refresh_s();stree.selection_set(str(j))
    wtree.bind("<<TreeviewSelect>>",load);stree.bind("<Double-1>",lambda _:edit_task())
    ttk.Button(lbuttons,text="New",command=new_workflow).pack(side="left");ttk.Button(lbuttons,text="Add Typed Example",command=add_example).pack(side="left",padx=4);ttk.Button(lbuttons,text="Delete",command=delete_workflow).pack(side="right")
    for text,cmd in (("Add Task",add_task),("Add Subworkflow",add_subworkflow),("Edit Item",edit_task),("Delete",delete_step),("Move Up",lambda:move(-1)),("Move Down",lambda:move(1))):ttk.Button(sbuttons,text=text,command=cmd).pack(side="left",padx=2)
    task_tab.columnconfigure(0,weight=1);task_tab.rowconfigure(0,weight=1);tt=ttk.Treeview(task_tab,columns=("task","ports","routes"),show="headings");tt.heading("task",text="Task");tt.heading("ports",text="Typed ports");tt.heading("routes",text="Implementation species / routes");tt.column("task",width=250);tt.column("ports",width=550);tt.column("routes",width=700);tt.grid(row=0,column=0,sticky="nsew",padx=8,pady=8)
    for t in tasks.values():tt.insert("","end",values=(t["id"],", ".join([*[f"in {k}:{v}" for k,v in t.get("inputs",{}).items()],*[f"out {k}:{v}" for k,v in t.get("outputs",{}).items()]]),", ".join(f"{x['id']} [{x['species']}]" for x in t["implementations"])))
    dt_tab.columnconfigure(0,weight=1);dt_tab.rowconfigure(0,weight=1);dt=ttk.Treeview(dt_tab,columns=("id","kind","meaning","relations"),show="headings")
    for c,h,w in (("id","Datatype",230),("kind","Kind",100),("meaning","Meaning",600),("relations","Relations",600)):dt.heading(c,text=h);dt.column(c,width=w)
    dt.grid(row=0,column=0,sticky="nsew",padx=8,pady=8)
    for x in datatypes:dt.insert("","end",values=(x["id"],x.get("kind"),x.get("description")," | ".join(f"{k}: {', '.join(x.get(k) or [])}" for k in ("extends","representations","aggregates") if x.get(k))))
    db=ttk.Frame(dt_tab);db.grid(row=1,column=0,sticky="ew",padx=8,pady=5);ttk.Button(db,text="Open Datatype Graph",command=lambda:open_path(GRAPH)).pack(side="left");ttk.Button(db,text="Open Manifest",command=lambda:open_path(DEFAULT_DATATYPE_PATH)).pack(side="left",padx=4);ttk.Button(db,text="Open Task Catalog",command=lambda:open_path(DEFAULT_TASK_PATH)).pack(side="left")
    def save(show=True):
        try:commit();validate_write(runner,path,raw);messagebox.showinfo("Saved","Typed workflows validated and saved.") if show else None;return True
        except Exception as e:messagebox.showerror("Save failed",str(e));return False
    def save_run():
        w=current();name=wid.get().strip()
        if w and name and save(False):root.destroy();LlmWorkflowEngine(runner).run(name)
    bottom=ttk.Frame(root);bottom.pack(fill="x",padx=10,pady=8);ttk.Button(bottom,text="Save",command=save).pack(side="left");ttk.Button(bottom,text="Save and Run Selected",command=save_run).pack(side="left",padx=4);ttk.Button(bottom,text="Edit Raw JSON",command=lambda:open_path(path)).pack(side="left");ttk.Button(bottom,text="Close",command=root.destroy).pack(side="right")
    refresh_w(0 if workflows else None);load() if workflows else None;root.mainloop()

def open_task_editor(runner):
    r=runner.llm_router()
    if not isinstance(r,TaskAwareWorkflowRouter):raise RuntimeError("Typed task router not installed")
    path=Path(r.workflow_path);raw=read_obj(path)
    if (os.getenv("METTAFLOW_WORKFLOW_DESKTOP") or os.getenv("ARC3_LLM_WORKFLOW_EDITOR","")).lower() in {"text","cli","console"}:return run_workflow_menu(runner)
    try:gui(runner,path,raw)
    except Exception as e:print(f"Typed workflow GUI unavailable ({e}); using text menu.");run_workflow_menu(runner)

def install_workflow_task_editor_ui(ui):
    if getattr(ui.read_key,"_arc3_task_editor",False):return
    old=ui.read_key;old_help=ui.print_controls
    def read_key():
        k=old()
        if k!="W":return k
        from multillm_runner import last_runner
        r=last_runner()
        try:open_task_editor(r) if r else print("No active ARC3 runner.")
        except Exception as e:print(f"Typed workflow editor error: {e}")
        return "\r"
    def help(r,rows):old_help(r,rows);print("Typed workflows: (W) tasks + typed slots + LLM/Prolog/Python routes + datatype graph")
    read_key._arc3_task_editor=True;ui.read_key=read_key;ui.print_controls=help
