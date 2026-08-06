import { useMemo } from "react";
import type { ArcObject } from "../artifacts/artifactTypes";

interface ArcGridProps {
  title?: string;
  grid: number[][];
  objects: ArcObject[];
  selectedObjectId?: string;
  onHoverObject?: (object?: ArcObject) => void;
  onSelectObject?: (object?: ArcObject) => void;
  showCoordinates?: boolean;
  compact?: boolean;
}

const ARC_COLORS = ["#05070b", "#2d8cff", "#ff3b4f", "#2dd36f", "#ffd54a", "#8c62ff", "#8b5a2b", "#ff8ad8", "#6ee7ff", "#b9c2cc"];

export function ArcGrid({ title = "ARC Scene", grid, objects, selectedObjectId, onHoverObject, onSelectObject, showCoordinates = false, compact = false }: ArcGridProps) {
  const objectMap = useMemo(() => {
    const map = new Map<string, ArcObject>();
    for (const object of objects) for (const [x, y] of object.cells) map.set(`${x}:${y}`, object);
    return map;
  }, [objects]);

  const columns = grid[0]?.length ?? 0;
  const cellSize = compact ? 22 : 40;

  return (
    <div className={`arc-viewer ${compact ? "arc-viewer--compact" : ""}`}>
      <div className="arc-viewer__toolbar"><strong>{title}</strong><span>{columns} × {grid.length}</span></div>
      <div className="arc-grid-wrap">
        {showCoordinates && <div className="axis axis--top">{Array.from({ length: columns }, (_, i) => <span key={i}>{i}</span>)}</div>}
        <div className="arc-grid" style={{ gridTemplateColumns: `repeat(${columns}, ${cellSize}px)` }} onMouseLeave={() => onHoverObject?.(undefined)}>
          {grid.flatMap((row, y) => row.map((color, x) => {
            const object = objectMap.get(`${x}:${y}`);
            const selected = object?.id === selectedObjectId;
            return <button key={`${x}:${y}`} type="button" className={`arc-cell ${selected ? "arc-cell--selected" : ""} ${object ? "arc-cell--object" : ""}`} style={{ width: cellSize, height: cellSize, background: ARC_COLORS[color] ?? ARC_COLORS[0] }} onMouseEnter={() => onHoverObject?.(object)} onClick={() => onSelectObject?.(object)} title={object ? `${object.name} (${x},${y})` : `Background (${x},${y})`} aria-label={`Cell ${x}, ${y}, color ${color}`} />;
          }))}
        </div>
      </div>
    </div>
  );
}
