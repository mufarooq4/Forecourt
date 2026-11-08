export type FuelGrade = "SUPER" | "HI_OCTANE" | "DIESEL";

export const FUEL_LABELS: Record<FuelGrade, string> = {
  SUPER: "Super",
  HI_OCTANE: "Hi-Oct",
  DIESEL: "Diesel",
};

export const FUEL_FULL_LABELS: Record<FuelGrade, string> = {
  SUPER: "Super (RON 92)",
  HI_OCTANE: "Hi-Octane (RON 97)",
  DIESEL: "Diesel (HSD)",
};

export function fuelFillClass(grade: FuelGrade): string {
  switch (grade) {
    case "SUPER":
      return "bg-super";
    case "HI_OCTANE":
      return "bg-hi-octane";
    case "DIESEL":
      return "bg-diesel";
  }
}

/** AA text colour tokens — never use fill colours for labels. */
export function fuelTextClass(grade: FuelGrade): string {
  switch (grade) {
    case "SUPER":
      return "text-super-text";
    case "HI_OCTANE":
      return "text-hi-octane-text";
    case "DIESEL":
      return "text-diesel-text";
  }
}
