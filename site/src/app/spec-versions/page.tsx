import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, CheckCircle2, Clock, Archive } from "lucide-react";
import { getListedSpecVersions, type SpecVersion } from "@/lib/spec-versions";

export const metadata: Metadata = {
  title: "Spec Versions — DPROD",
  description:
    "All available versions of the DPROD specification: the frozen OMG 1.0, the current develop draft, and every in-flight ballot branch.",
};

// Render per-request so the Vercel API call in getSpecVersions() always
// happens with real env vars (build-time has none → empty list). The
// underlying fetch still caches for 60s via `next: { revalidate: 60 }` so
// repeated page views in the same window don't spam the Vercel API.
export const dynamic = "force-dynamic";

function IconFor({ version }: { version: SpecVersion }) {
  if (version.kind === "archive") {
    return <Archive className="h-6 w-6 text-[#ff6f00]" />;
  }
  if (version.isProduction) {
    return <CheckCircle2 className="h-6 w-6 text-[#4051b5]" />;
  }
  return <Clock className="h-6 w-6 text-muted-foreground" />;
}

function BadgeFor({ version }: { version: SpecVersion }) {
  if (version.kind === "archive") {
    return (
      <span className="inline-flex items-center rounded-full border border-[#ff6f00]/30 bg-[#ff6f00]/5 px-2 py-0.5 text-xs font-semibold uppercase tracking-widest text-[#ff6f00]">
        Frozen · Normative
      </span>
    );
  }
  if (version.isProduction) {
    return (
      <span className="inline-flex items-center rounded-full border border-[#4051b5]/30 bg-[#4051b5]/5 px-2 py-0.5 text-xs font-semibold uppercase tracking-widest text-[#4051b5]">
        Production
      </span>
    );
  }
  return (
    <span className="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
      Preview
    </span>
  );
}

export default async function SpecVersionsPage() {
  // Deliberately the *listed* set, not the routable one: a branch that no
  // longer exists must not be advertised, even though its preview URL still
  // resolves. See issue #249.
  const { versions, complete } = await getListedSpecVersions();

  return (
    <div className="flex flex-col">
      {/* Page header */}
      <section className="border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-20 md:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              Specification
            </p>
            <h1 className="mb-6 text-4xl font-black tracking-tighter md:text-6xl">
              Spec versions
            </h1>
            <p className="text-xl text-muted-foreground md:text-2xl">
              The frozen OMG 1.0, the current working draft, and every
              in-flight ballot preview — all at stable URLs on this domain.
            </p>
          </div>
        </div>
      </section>

      {/* Version list */}
      <section>
        <div className="container py-20">
          <div className="mx-auto max-w-4xl">
            {!complete && (
              <div className="mb-6 rounded-lg border border-[#ff6f00]/40 bg-[#ff6f00]/5 p-4 text-sm">
                <p className="font-semibold text-foreground">
                  Branch list unavailable
                </p>
                <p className="mt-1 text-muted-foreground">
                  The GitHub lookup that checks which branches still exist did
                  not succeed, so only the archive and the production draft are
                  listed. In-flight preview branches are hidden rather than
                  shown unverified. The deployment logs record the reason.
                </p>
              </div>
            )}

            <div className="space-y-4">
              {versions.map((version) => {
                const href =
                  version.kind === "archive" ? "/spec/main" : `/spec/${version.id}`;
                return (
                  <Link
                    key={version.id}
                    href={href}
                    className="group block rounded-lg border p-6 transition-colors hover:border-[#4051b5]/50 hover:bg-[#4051b5]/5"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:gap-6">
                      <div className="shrink-0">
                        <IconFor version={version} />
                      </div>
                      <div className="flex-1">
                        <div className="mb-2 flex flex-wrap items-center gap-3">
                          <h2 className="text-xl font-bold">{version.label}</h2>
                          <BadgeFor version={version} />
                        </div>
                        <p className="mb-2 text-muted-foreground">
                          {version.description}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          <span className="font-mono">{href}</span>
                          {version.kind === "vercel-branch" && (
                            <>
                              {" · branch "}
                              <span className="font-mono">{version.branch}</span>
                            </>
                          )}
                        </p>
                      </div>
                      <ArrowRight className="mt-1 h-5 w-5 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-[#4051b5]" />
                    </div>
                  </Link>
                );
              })}
            </div>

            <div className="mt-12 rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
              <p className="mb-2 font-semibold text-foreground">How it works</p>
              <p>
                Every branch in the repository automatically gets its own
                Vercel preview deployment. This page queries the Vercel API at
                request time (cached for 60&nbsp;seconds) so new branches show
                up without needing to redeploy <code>develop</code>, and
                cross-checks GitHub so that branches which have since been
                deleted drop off the list. Each version link routes through
                Next.js middleware to the correct deployment&apos;s own{" "}
                <code>/spec/</code> page.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
