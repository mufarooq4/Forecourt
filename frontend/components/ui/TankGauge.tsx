import { AlertTriangle } from "lucide-react";
import {
  FUEL_LABELS,
  fuelFillClass,
  fuelTextClass,
  type FuelGrade,
} from "@/lib/fuel";
import { formatDaysLeft, formatLitres } from "@/lib/format";

export interface TankGaugeProps {
  fuelGrade: FuelGrade;
  capacityL: number;
  currentL: number;
  /** When provided and level is below 20%, shown as the warning line. */
  daysOfStock?: number;
  /** Compact mode for dense table cells. */
  size?: "sm" | "md";
  className?: string;
  /** Hide the grade label when a nearby column already names it. Default false — always show. */
  showLabel?: boolean;
}

const LOW_STOCK_RATIO = 0.2;

export function TankGauge({
  fuelGrade,
  capacityL,
  currentL,
  daysOfStock,
  size = "md",
  className = "",
  showLabel = true,
}: TankGaugeProps) {
  const safeCapacity = capacityL > 0 ? capacityL : 1;
  const clamped = Math.min(Math.max(currentL, 0), safeCapacity);
  const pct = (clamped / safeCapacity) * 100;
  const isLow = pct < LOW_STOCK_RATIO * 100;
  const label = FUEL_LABELS[fuelGrade];
  const trackH = size === "sm" ? "h-2" : "h-3";
  const labelSize = size === "sm" ? "text-xs" : "text-sm";

  const warningText =
    daysOfStock !== undefined
      ? formatDaysLeft(daysOfStock)
      : `${formatLitres(clamped)} L left`;

  return (
    <div className={`min-w-0 ${className}`}>
      <div className={`mb-1 flex items-baseline justify-between gap-2 ${labelSize}`}>
        {showLabel ? (
          <span className={`font-semibold ${fuelTextClass(fuelGrade)}`}>
            {label}
          </span>
        ) : (
          <span className="sr-only">{label}</span>
        )}
        <span className="tabular text-ink-muted">
          {formatLitres(clamped)}
          <span> / </span>
          {formatLitres(safeCapacity)}
          <span className="ml-0.5">L</span>
        </span>
      </div>

      <div
        className={`relative w-full overflow-hidden border border-ink-muted bg-slab ${trackH}`}
        role="meter"
        aria-label={`${label} tank level`}
        aria-valuemin={0}
        aria-valuemax={safeCapacity}
        aria-valuenow={clamped}
        aria-valuetext={`${formatLitres(clamped)} of ${formatLitres(safeCapacity)} litres${isLow ? `, low stock, ${warningText}` : ""}`}
      >
        {/* Fill */}
        <div
          className={`absolute inset-y-0 left-0 ${fuelFillClass(fuelGrade)}`}
          style={{ width: `${pct}%` }}
        />

        {/* Empty hatch only when below 20% */}
        {isLow ? (
          <div
            className="hazard-hatch absolute inset-y-0 right-0"
            style={{ width: `${100 - pct}%` }}
            aria-hidden="true"
          />
        ) : null}

        {/* 20% tick: 2px ink with 1px canopy gaps so it reads over hatch */}
        <div
          className="absolute inset-y-0 z-10 flex"
          style={{ left: `calc(${LOW_STOCK_RATIO * 100}% - 2px)` }}
          aria-hidden="true"
        >
          <span className="w-px self-stretch bg-canopy" />
          <span className="w-0.5 self-stretch bg-ink" />
          <span className="w-px self-stretch bg-canopy" />
        </div>
      </div>

      {isLow ? (
        <p className="mt-1 flex items-start gap-1 text-xs text-ink">
          <AlertTriangle
            className="mt-0.5 h-3 w-3 shrink-0"
            aria-hidden="true"
            strokeWidth={2}
          />
          <span>{warningText}</span>
        </p>
      ) : null}
    </div>
  );
}
