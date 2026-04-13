"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export type EkgfLogoSymbolProps = React.SVGProps<SVGSVGElement> & {
  title?: string;
};

export function EkgfLogoSymbol({
  className,
  title = "EKGF Logo",
  ...props
}: EkgfLogoSymbolProps) {
  return (
    <svg
      // Tighten the viewBox to the actual drawn bounds so the symbol centers
      // nicely next to "EKGF" without needing big translate hacks.
      viewBox="12 30 170 170"
      role="img"
      aria-label={title}
      xmlns="http://www.w3.org/2000/svg"
      className={cn("shrink-0", className)}
      {...props}
    >
      <title>{title}</title>
      <g fill="#ff9900">
        <circle cx="30" cy="60" r="12" />
        <circle cx="80" cy="40" r="7" />
        <circle cx="125" cy="40" r="7" />
        <circle cx="170" cy="80" r="12" />
        <circle cx="170" cy="150" r="12" />
        <circle cx="100" cy="180" r="12" />
        <circle cx="50" cy="150" r="18" />
        <circle cx="100" cy="100" r="18" />
      </g>

      <g strokeWidth="2.2" stroke="#ff9900">
        <line x1="100" y1="100" x2="30" y2="60" />
        <line x1="100" y1="100" x2="80" y2="40" />
        <line x1="100" y1="100" x2="125" y2="40" />
        <line x1="125" y1="40" x2="170" y2="80" />
        <line x1="100" y1="100" x2="50" y2="150" />
        <line x1="100" y1="100" x2="170" y2="150" />
        <line x1="100" y1="180" x2="170" y2="150" />
        <line x1="170" y1="80" x2="170" y2="150" />
        <line x1="100" y1="180" x2="50" y2="150" />
      </g>
    </svg>
  );
}
