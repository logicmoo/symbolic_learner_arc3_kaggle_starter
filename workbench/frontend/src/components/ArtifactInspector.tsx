import { Boxes, GitBranch, History, Sparkles } from "lucide-react";
import type { ArcObject } from "../artifacts/artifactTypes";

export function ArtifactInspector({ object }: { object?: ArcObject }) {
  return <aside className="artifact-inspector panel">
    <div className="panel-heading"><div><span className="eyebrow">Semantic bundle</span><h2>Artifact Inspector</h2></div><Boxes size={20}/></div>
    {!object ? <div className="empty-state"><Sparkles size={30}/><h3>Select an object</h3><p>Hover or click cells in the ARC view to inspect all linked representations.</p></div> : <>
      <section className="inspector-card"><div className="inspector-title"><div><span className="object-dot" style={{ background: object.color === 1 ? "#2d8cff" : "#ff3b4f" }}/><h3>{object.name}</h3></div><span className="confidence">{Math.round(object.confidence*100)}%</span></div><code>{object.id}</code><div className="semantic-tags"><span>Individual Object</span><span>Image</span><span>Turtle</span><span>Prolog</span></div></section>
      <section><h3 className="section-title"><GitBranch size={15}/> Properties</h3><dl className="property-list">{Object.entries(object.properties).map(([k,v]) => <div key={k}><dt>{k}</dt><dd>{String(v)}</dd></div>)}</dl></section>
      <section><h3 className="section-title"><Boxes size={15}/> Relationships</h3><ul className="relationship-list"><li><b>contained by</b> scene-ls20-0-0</li><li><b>derived from</b> input-image-0001</li><li><b>represented by</b> turtle-{object.id}</li><li><b>represented by</b> facts-{object.id}</li></ul></section>
      <section><h3 className="section-title"><History size={15}/> Provenance</h3><dl className="property-list"><div><dt>Created by</dt><dd>turtlize_objects</dd></div><div><dt>Model</dt><dd>symbolic-object-extractor</dd></div><div><dt>Status</dt><dd className="verified">verified</dd></div></dl></section>
    </>}
  </aside>;
}
