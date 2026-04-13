import type { Metadata } from "next";
import {
  CheckCircle2,
  Circle,
  Clock,
  GitBranch,
  Vote,
  Sparkles,
} from "lucide-react";

export const metadata: Metadata = {
  title: "Roadmap — DPROD",
  description:
    "Where DPROD came from, what's in flight today, and how the OMG ballot process shapes the evolution of the standard.",
};

type Status = "done" | "in-progress" | "planned";

const STATUS_META: Record<
  Status,
  { icon: typeof CheckCircle2; color: string; label: string }
> = {
  done: {
    icon: CheckCircle2,
    color: "#4051b5",
    label: "Done",
  },
  "in-progress": {
    icon: Clock,
    color: "#ff6f00",
    label: "In progress",
  },
  planned: {
    icon: Circle,
    color: "rgb(100 116 139)",
    label: "Planned",
  },
};

const TIMELINE: Array<{
  status: Status;
  date: string;
  title: string;
  description: string;
}> = [
  {
    status: "done",
    date: "2024",
    title: "DPROD 1.0 published for public comment",
    description:
      "OMG released the DPROD proposed specification as part of its standardisation process. The 1.0 version is frozen and serves as the official reference point.",
  },
  {
    status: "done",
    date: "2024",
    title: "OMG Request for Comments completed",
    description:
      "Community feedback gathered through the OMG RFC cycle informed a backlog of improvements now being addressed in subsequent ballots.",
  },
  {
    status: "in-progress",
    date: "Ballot 4",
    title: "Modelling and clarity improvements",
    description:
      "Fixes to class identifiers in the generated spec, protocol modelling, lifecycle status values, SHACL shape hygiene, and worked examples for data rights. Approved individual issues are bundled for a single vote.",
  },
  {
    status: "planned",
    date: "Later ballots",
    title: "Deeper alignment and new examples",
    description:
      "More worked examples, tighter alignment with neighbouring OMG and W3C vocabularies, and tooling improvements. Priorities are set by the working group and driven by community issues.",
  },
];

export default function RoadmapPage() {
  return (
    <div className="flex flex-col">
      {/* Page header */}
      <section className="border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-20 md:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              Work in progress
            </p>
            <h1 className="mb-6 text-4xl font-black tracking-tighter md:text-6xl">
              Roadmap
            </h1>
            <p className="text-xl text-muted-foreground md:text-2xl">
              DPROD evolves through formal OMG ballots. Here is where it has
              been, where it is now, and how the process works.
            </p>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-4xl">
            <h2 className="mb-10 text-3xl font-bold">Timeline</h2>
            <ol className="relative space-y-10 border-l border-border/60 pl-8">
              {TIMELINE.map(({ status, date, title, description }) => {
                const meta = STATUS_META[status];
                const Icon = meta.icon;
                return (
                  <li key={title} className="relative">
                    <span
                      className="absolute -left-[2.4rem] flex h-8 w-8 items-center justify-center rounded-full border bg-background"
                      style={{ borderColor: meta.color }}
                    >
                      <Icon
                        className="h-4 w-4"
                        style={{ color: meta.color }}
                      />
                    </span>
                    <div className="mb-1 flex flex-wrap items-center gap-3">
                      <span
                        className="text-xs font-semibold uppercase tracking-widest"
                        style={{ color: meta.color }}
                      >
                        {meta.label}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {date}
                      </span>
                    </div>
                    <h3 className="mb-2 text-xl font-bold">{title}</h3>
                    <p className="text-muted-foreground">{description}</p>
                  </li>
                );
              })}
            </ol>
          </div>
        </div>
      </section>

      {/* How ballots work */}
      <section>
        <div className="container py-20">
          <div className="mx-auto max-w-4xl">
            <h2 className="mb-10 text-3xl font-bold">
              How the OMG ballot process works
            </h2>
            <div className="space-y-6">
              <div className="flex gap-4 rounded-lg border p-6">
                <GitBranch className="h-8 w-8 shrink-0 text-[#4051b5]" />
                <div>
                  <h3 className="mb-1 text-lg font-semibold">
                    Issues become branches
                  </h3>
                  <p className="text-muted-foreground">
                    Every improvement is tracked as an OMG JIRA issue and
                    implemented on its own Git branch named after the issue
                    (e.g. <code className="text-sm">DPROD-21</code>). This
                    keeps individual changes reviewable in isolation.
                  </p>
                </div>
              </div>

              <div className="flex gap-4 rounded-lg border p-6">
                <Sparkles className="h-8 w-8 shrink-0 text-[#ff6f00]" />
                <div>
                  <h3 className="mb-1 text-lg font-semibold">
                    Issue branches land on <code className="text-base">develop</code>
                  </h3>
                  <p className="text-muted-foreground">
                    Once an issue is approved by the working group, the
                    branch is merged into <code className="text-sm">develop</code>.
                    The <code className="text-sm">develop</code> branch always
                    reflects the current working draft of the standard.
                  </p>
                </div>
              </div>

              <div className="flex gap-4 rounded-lg border p-6">
                <Vote className="h-8 w-8 shrink-0 text-[#4051b5]" />
                <div>
                  <h3 className="mb-1 text-lg font-semibold">
                    Ballots bundle issues for a formal vote
                  </h3>
                  <p className="text-muted-foreground">
                    When enough issues are ready, a ballot branch
                    (e.g. <code className="text-sm">ballot/4</code>) gathers
                    them for a single OMG vote. Bundling preserves individual
                    issue history while giving the membership one thing to
                    vote on.
                  </p>
                </div>
              </div>

              <div className="flex gap-4 rounded-lg border p-6">
                <CheckCircle2 className="h-8 w-8 shrink-0 text-[#ff6f00]" />
                <div>
                  <h3 className="mb-1 text-lg font-semibold">
                    Approved ballots update the standard
                  </h3>
                  <p className="text-muted-foreground">
                    A passing ballot merges into the canonical branch and the
                    bundled changes become part of the next official version
                    of DPROD.
                  </p>
                </div>
              </div>
            </div>

            <p className="mt-10 rounded-lg border border-dashed p-6 text-sm text-muted-foreground">
              This page is intentionally a placeholder for the phase-1 site.
              A more detailed roadmap, with linked issues and target
              versions, will replace it once the working group signs off on
              the public milestones.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
