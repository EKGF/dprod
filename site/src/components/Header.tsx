"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { Moon, Sun, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EkgfLogoSymbol } from "@/components/icons/EkgfLogoSymbol";
import { OmgLogo } from "@/components/icons/OmgLogo";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

/**
 * Items that belong to the EKGF primary zone (ekgf.org). They're rendered
 * as plain `<a>` tags with root-relative hrefs so the Next.js basePath
 * ("/dprod") is NOT prepended — clicking these escapes the dprod zone
 * back to the ekgf.org routes that serve them.
 */
const EKGF_NAV = [
  { href: "/about", label: "About" },
  { href: "/quadrants", label: "Quadrants" },
  { href: "/resources", label: "Resources" },
  { href: "/membership", label: "Membership" },
  { href: "/contact", label: "Contact" },
] as const;

/**
 * Items that live inside this zone. Rendered with Next.js `<Link>` so the
 * "/dprod" basePath is automatically prepended.
 */
const DPROD_NAV = [
  { href: "/spec-versions", label: "Specification" },
] as const;

export function Header() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/20 bg-background/90">
      <div className="container flex h-20 items-center justify-between">
        <div className="flex items-center gap-8">
          {/* Brand link escapes the dprod zone back to ekgf.org root. */}
          <a
            href="/"
            className="group flex items-center text-3xl leading-none transform -translate-y-1.5"
          >
            <span className="relative inline-flex items-baseline">
              <EkgfLogoSymbol className="absolute right-full mr-2 h-[1em] w-[1em] transition-transform group-hover:scale-110" />
              <span className="hidden font-black tracking-tighter leading-none sm:inline-block">
                EKGF
              </span>
            </span>
          </a>

          <NavigationMenu className="hidden md:flex">
            <NavigationMenuList>
              {EKGF_NAV.map(({ href, label }) => (
                <NavigationMenuItem key={href}>
                  <NavigationMenuLink
                    asChild
                    className={navigationMenuTriggerStyle()}
                  >
                    <a href={href}>{label}</a>
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
              {DPROD_NAV.map(({ href, label }) => (
                <NavigationMenuItem key={href}>
                  <NavigationMenuLink
                    asChild
                    className={navigationMenuTriggerStyle()}
                  >
                    <Link href={href}>{label}</Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
          >
            <Moon className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Sun className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
          <Button asChild variant="ghost" size="icon" className="hidden sm:flex">
            <a
              href="https://github.com/EKGF/dprod"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
            >
              <Github className="h-5 w-5" />
            </a>
          </Button>

          <a
            href="https://omg.org"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Object Management Group (OMG)"
            className="hidden sm:flex items-center rounded-md px-2 py-1 opacity-80 hover:opacity-100 transition-opacity transform -translate-y-1"
          >
            <OmgLogo className="h-[1.65rem] w-auto" />
          </a>
        </div>
      </div>
    </header>
  );
}
