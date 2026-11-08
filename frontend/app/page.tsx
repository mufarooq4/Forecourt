import { TankGauge } from "@/components/ui/TankGauge";

/**
 * Step 1 review surface: shell + tokens + TankGauge samples.
 * Real Overview lands in step 3.
 */
export default function Step1ReviewPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-extrabold tracking-tight text-ink sm:text-3xl">
          Forecourt
        </h1>
        <p className="mt-1 max-w-xl text-sm text-ink-muted sm:text-base">
          Step 1 review: tokens, layout shell, and tank gauges. Sample levels
          only — mock data arrives in step 2.
        </p>
      </header>

      <section aria-labelledby="palette-heading" className="space-y-3">
        <h2 id="palette-heading" className="text-lg font-semibold text-ink">
          Colour tokens
        </h2>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-5">
          {(
            [
              ["canopy", "bg-canopy"],
              ["slab", "bg-slab"],
              ["line", "bg-line"],
              ["ink", "bg-ink"],
              ["ink-muted", "bg-ink-muted"],
            ] as const
          ).map(([name, cls]) => (
            <div key={name} className="border border-line">
              <div className={`h-12 border-b border-line ${cls}`} />
              <p className="px-2 py-1.5 text-xs text-ink">{name}</p>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {(
            [
              ["Super", "bg-super", "text-super-text"],
              ["Hi-Oct", "bg-hi-octane", "text-hi-octane-text"],
              ["Diesel", "bg-diesel", "text-diesel-text"],
            ] as const
          ).map(([label, bg, text]) => (
            <div
              key={label}
              className="flex items-center gap-3 border border-line bg-slab px-3 py-2"
            >
              <span className={`h-4 w-8 ${bg}`} aria-hidden="true" />
              <span className={`text-sm font-semibold ${text}`}>{label}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-labelledby="gauge-heading" className="space-y-4">
        <h2 id="gauge-heading" className="text-lg font-semibold text-ink">
          Tank gauges
        </h2>
        <p className="text-sm text-ink-muted">
          Thin tick at 20%. Hatch on the empty track only when below that mark.
          Grade name is always visible with the fill.
        </p>

        <div className="space-y-6 border border-line bg-canopy p-4 sm:p-6">
          <TankGauge
            fuelGrade="SUPER"
            capacityL={30000}
            currentL={18400}
            daysOfStock={6.2}
          />
          <TankGauge
            fuelGrade="HI_OCTANE"
            capacityL={20000}
            currentL={9200}
            daysOfStock={4.1}
            size="sm"
          />
          <TankGauge
            fuelGrade="DIESEL"
            capacityL={40000}
            currentL={5400}
            daysOfStock={2.5}
          />
        </div>

        <div className="border border-line">
          <div className="border-b border-line bg-slab px-3 py-2 text-sm font-semibold text-ink">
            Mini gauges in a dense row (table-cell preview)
          </div>
          <div className="grid gap-4 p-3 sm:grid-cols-3">
            <TankGauge
              fuelGrade="SUPER"
              capacityL={25000}
              currentL={21000}
              size="sm"
            />
            <TankGauge
              fuelGrade="HI_OCTANE"
              capacityL={18000}
              currentL={3100}
              daysOfStock={1.8}
              size="sm"
            />
            <TankGauge
              fuelGrade="DIESEL"
              capacityL={35000}
              currentL={28000}
              size="sm"
            />
          </div>
        </div>
      </section>

      <section aria-labelledby="type-heading" className="space-y-2">
        <h2 id="type-heading" className="text-lg font-semibold text-ink">
          Type and figures
        </h2>
        <p className="text-base text-ink">
          Overpass 400 body.{" "}
          <span className="font-semibold">Semibold 600</span>.{" "}
          <span className="font-extrabold">Extrabold 800</span>.
        </p>
        <p className="tabular text-2xl font-extrabold text-ink">
          12 400 L
        </p>
        <p className="tabular text-lg font-semibold text-ink">
          Rs 2.48 lakh
        </p>
        <p className="text-sm text-ink-muted">
          Recon status copy for later pages: Balanced / N tanks off
        </p>
      </section>
    </div>
  );
}
