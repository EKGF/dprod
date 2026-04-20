import Link from "next/link";
import { Github } from "lucide-react";

/**
 * Cross-zone nav items that escape the /dprod basePath back to ekgf.org.
 * Rendered as plain `<a>` tags.
 */
const EKGF_LINKS = [
  { href: "/about", label: "About" },
  { href: "/quadrants", label: "Quadrants" },
  { href: "/resources", label: "Resources" },
  { href: "/membership", label: "Membership" },
  { href: "/contact", label: "Contact" },
];

/** In-zone links rendered with Next.js Link (basePath auto-prefixed). */
const DPROD_LINKS = [
  { href: "/spec-versions", label: "Specification" },
];

const EXTERNAL_LINKS = [
  {
    href: "https://github.com/EKGF/dprod",
    label: "GitHub",
    icon: <Github className="h-4 w-4" />,
  },
  { href: "https://ekgf.org", label: "EKGF" },
  { href: "https://omg.org", label: "OMG" },
];

export function Footer() {
  return (
    <footer className="border-t border-border/20 bg-background/50">
      <div className="container py-12 md:py-16">
        <div className="grid gap-8 sm:grid-cols-2 md:grid-cols-3">
          <div>
            <h3 className="mb-4 text-lg font-semibold">DPROD</h3>
            <p className="text-sm text-muted-foreground">
              The Data Product Ontology — an OMG standard for describing
              Data Products using W3C Linked Data technologies.
            </p>
          </div>

          <div>
            <h3 className="mb-4 text-lg font-semibold">Navigate</h3>
            <ul className="space-y-2 text-sm">
              {EKGF_LINKS.map(({ href, label }) => (
                <li key={href}>
                  <a
                    href={href}
                    className="text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {label}
                  </a>
                </li>
              ))}
              {DPROD_LINKS.map(({ href, label }) => (
                <li key={href}>
                  <Link
                    href={href}
                    className="text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-lg font-semibold">Links</h3>
            <ul className="space-y-2 text-sm">
              {EXTERNAL_LINKS.map(({ href, label, icon }) => (
                <li key={href}>
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {icon}
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>Copyright © {new Date().getFullYear()} EDM Council, Inc.</p>
          <p className="mt-1">
            A standard of the{" "}
            <a
              href="https://omg.org"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-foreground"
            >
              Object Management Group (OMG)
            </a>
            {" · "}
            Developed by the{" "}
            <a
              href="https://ekgf.org"
              target="_blank"
              rel="noopener noreferrer"
              className="transition-colors hover:text-foreground"
            >
              Enterprise Knowledge Graph Forum (EKGF)
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
