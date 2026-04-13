import type { Metadata } from "next";
import {
  Users,
  Megaphone,
  AlertTriangle,
  Search,
  Plug,
  Layers,
  ExternalLink,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Why DPROD — Motivation & Background",
  description:
    "Why the OMG developed the Data Product Ontology: to solve inconsistent metadata, limited discoverability, and interoperability challenges in decentralized data architectures.",
};

const W3C_STACK = [
  {
    name: "DCAT",
    full: "Data Catalog Vocabulary",
    href: "https://www.w3.org/TR/vocab-dcat-3/",
    color: "#4051b5",
    description:
      "The W3C vocabulary DPROD extends. Provides the core building blocks for describing datasets, distributions, and data services — which DPROD profiles and specialises for data products.",
  },
  {
    name: "RDF",
    full: "Resource Description Framework",
    href: "https://www.w3.org/RDF/",
    color: "#ff6f00",
    description:
      "The graph data model that lets every DPROD concept be identified by a URI and linked to concepts from other vocabularies without translation layers.",
  },
  {
    name: "OWL",
    full: "Web Ontology Language",
    href: "https://www.w3.org/OWL/",
    color: "#4051b5",
    description:
      "The formal logic layer DPROD uses to define classes and properties with precise semantics — so tools can reason about data products, not just store records about them.",
  },
  {
    name: "SHACL",
    full: "Shapes Constraint Language",
    href: "https://www.w3.org/TR/shacl/",
    color: "#ff6f00",
    description:
      "The validation layer. DPROD ships SHACL shapes that let any tool verify whether a data product description conforms to the standard — no custom validators required.",
  },
  {
    name: "PROV",
    full: "Provenance Vocabulary",
    href: "https://www.w3.org/TR/prov-o/",
    color: "#4051b5",
    description:
      "The lineage layer. PROV lets DPROD describe how data products were produced, by whom, and from which inputs — essential for trust, audit, and compliance.",
  },
];

const PROBLEMS = [
  {
    icon: AlertTriangle,
    color: "#ff6f00",
    title: "Inconsistent metadata",
    description:
      "Every platform, every team, every vendor describes data products differently. Without a shared schema, consumers spend more time reconciling metadata than using the data.",
  },
  {
    icon: Search,
    color: "#4051b5",
    title: "Limited discoverability",
    description:
      "Data products exist in silos. Without standard descriptions, there is no federated search, no cross-domain catalog, and no way for consumers to find what already exists.",
  },
  {
    icon: Plug,
    color: "#ff6f00",
    title: "Interoperability friction",
    description:
      "Data products built on incompatible descriptions cannot be composed. DPROD lets a data product produced on one platform be described, understood, and consumed on another — without rewriting metadata.",
  },
];

export default function WhyPage() {
  return (
    <div className="flex flex-col">
      {/* Page header */}
      <section className="border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-20 md:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              Motivation
            </p>
            <h1 className="mb-6 text-4xl font-black tracking-tighter md:text-6xl">
              Why DPROD?
            </h1>
            <p className="text-xl text-muted-foreground md:text-2xl">
              As organisations adopt Data Mesh and other decentralised data
              architectures, they discover the same problems over and over.
              DPROD exists to solve them once, as a standard.
            </p>
          </div>
        </div>
      </section>

      {/* Problem DPROD solves */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-10 text-3xl font-bold">
              The problem DPROD solves
            </h2>
            <div className="grid gap-6 md:grid-cols-3">
              {PROBLEMS.map(({ icon: Icon, color, title, description }) => (
                <Card key={title}>
                  <CardHeader>
                    <Icon
                      className="mb-2 h-10 w-10"
                      style={{ color }}
                    />
                    <CardTitle>{title}</CardTitle>
                    <CardDescription className="mt-2 text-base">
                      {description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Origins & Standardisation */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-10 text-3xl font-bold">
              Origins &amp; standardisation
            </h2>
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <Users className="mb-2 h-10 w-10 text-[#4051b5]" />
                  <CardTitle>Working Group Leadership</CardTitle>
                  <CardDescription className="mt-2 text-base">
                    DPROD is developed in the EKGF community and edited by{" "}
                    <a
                      href="https://www.linkedin.com/in/tonyseale/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Tony Seale (Chair)
                    </a>{" "}
                    together with editors including Natasa Varytimou, Pete
                    Rivett, and Marcel Fröhlich. Setting up the DPROD working
                    group was an initiative by{" "}
                    <a
                      href="https://www.linkedin.com/in/jgeluk/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Jacobus Geluk
                    </a>
                    .
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <Megaphone className="mb-2 h-10 w-10 text-[#ff6f00]" />
                  <CardTitle>OMG Request for Comments</CardTitle>
                  <CardDescription className="mt-2 text-base">
                    OMG published the DPROD proposed specification for public
                    comment as part of its standardisation process, focused on
                    improving discoverability, interoperability, and reducing
                    vendor lock-in across data marketplaces.{" "}
                    <a
                      href="https://www.omg.org/news/releases/pr2024/09-24-24.htm"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Read the OMG release
                      <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Built on W3C standards */}
      <section>
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <div className="mb-10 flex items-center gap-3">
              <Layers className="h-8 w-8 text-[#4051b5]" />
              <h2 className="text-3xl font-bold">Built on W3C standards</h2>
            </div>
            <p className="mb-10 max-w-3xl text-lg text-muted-foreground">
              DPROD does not reinvent the wheel. It profiles a stack of
              established W3C standards so data products inherit decades of
              work on semantics, validation, and interoperability.
            </p>
            <div className="space-y-4">
              {W3C_STACK.map(({ name, full, href, color, description }) => (
                <a
                  key={name}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group block rounded-lg border p-6 transition-colors hover:border-[#4051b5]/50 hover:bg-[#4051b5]/5"
                >
                  <div className="flex flex-col gap-2 md:flex-row md:items-start md:gap-6">
                    <div className="md:w-40 md:shrink-0">
                      <div
                        className="text-2xl font-black tracking-tight"
                        style={{ color }}
                      >
                        {name}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {full}
                      </div>
                    </div>
                    <p className="flex-1 text-muted-foreground">
                      {description}
                    </p>
                    <ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
