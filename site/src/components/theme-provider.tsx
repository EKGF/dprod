"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider, useTheme } from "next-themes";

function getCookie(name: string) {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(
    new RegExp(`(^|;\\s*)${name}=([^;]*)`),
  );
  return match ? decodeURIComponent(match[2]) : "";
}

function setCookie(name: string, value: string) {
  if (typeof document === "undefined") return;
  const host = typeof window !== "undefined" ? window.location.hostname : "";
  const domain =
    host === "ekgf.org" || host.endsWith(".ekgf.org")
      ? "; domain=.ekgf.org"
      : "";
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=31536000; samesite=lax${domain}`;
}

function ThemeCookieSync() {
  const { theme, setTheme } = useTheme();

  React.useEffect(() => {
    const cookieTheme = getCookie("ekgf-theme");
    if (cookieTheme === "dark" || cookieTheme === "light") {
      setTheme(cookieTheme);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  React.useEffect(() => {
    if (theme === "dark" || theme === "light") {
      setCookie("ekgf-theme", theme);
    }
  }, [theme]);

  return null;
}

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return (
    <NextThemesProvider {...props}>
      <ThemeCookieSync />
      {children}
    </NextThemesProvider>
  );
}
