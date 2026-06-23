import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { DataType } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatValue(
  value: number | string | null,
  dataType: DataType | null,
  formatString?: string | null
): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "string") return value;

  const num = Number(value);
  if (isNaN(num)) return String(value);

  if (dataType === "percentage" || formatString?.includes("%")) {
    return `${(num * (Math.abs(num) <= 1 ? 100 : 1)).toFixed(1)}%`;
  }
  if (
    dataType === "currency" ||
    formatString?.includes("$") ||
    formatString?.includes("€")
  ) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(num);
  }
  if (Math.abs(num) >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  }
  if (Math.abs(num) >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return num.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

export function isNumeric(value: unknown): value is number {
  return typeof value === "number" && !isNaN(value);
}

export function getValueColor(value: number | string | null): string {
  if (!isNumeric(value)) return "text-surface-200";
  if (value > 0) return "text-brand-emerald";
  if (value < 0) return "text-brand-rose";
  return "text-surface-400";
}
