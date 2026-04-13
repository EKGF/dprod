import type { Metadata } from "next";
import Link from "next/link";
import {
  Package,
  Plug,
  Database,
  FileBox,
  Network,
  Store,
  Cloud,
  Shield,
  ArrowRight,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Core Concepts — DPROD",
  description:
    "The core concepts of the Data Product Ontology: Data Product, Ports (Data Services), Distributions & Datasets, and the use cases DPROD enables.",
};

const CONCEPTS = [
  {
    icon: Package,
    color: "#4051b5",
    title: "Data Product",
    description:
      "A rational, managed, and governed collection of data with purpose, value, and ownership, meeting consumer needs over a planned lifecycle. Data products have input and output ports, code, and metadata.",
    anchor: "dataproductshape",
  },
  {
    icon: Plug,
    color: "#ff6f00",
    title: "Ports (Data Services)",
    description:
      "Digital interfaces that provide access to datasets. Input ports bring data into the product, while output ports share generated data. Ports specify connection details, formats, and link to datasets with shared schemas.",
    anchor: "dataserviceshape",
  },
  {
    icon: Database,
    color: "#4051b5",
    title: "Distributions",
    description:
      "Physical representations of data — CSV, JSON, Parquet, and access methods. A single dataset may have multiple distributions to serve different consumer needs without duplicating the underlying information.",
    anchor: "distributionshape",
  },
  {
    icon: FileBox,
    color: "#ff6f00",
    title: "Datasets",
    description:
      "Logical models of the data that can conform to shared standards like FIBO, CDM, or custom ontologies using SHACL or OWL. The schema lives with the data, not in out-of-band documentation.",
    anchor: "datasetshape",
  },
];

const USE_CASES = [
  {
    icon: Network,
    color: "#4051b5",
    title: "Data Mesh Implementation",
    description:
      "Enable domain-oriented decentralised data ownership with standardised product descriptions. Every domain publishes its data products in the same machine-readable format.",
  },
  {
    icon: Store,
    color: "#ff6f00",
    title: "Data Marketplaces",
    description:
      "Build internal or external data marketplaces with discoverable, well-described data products. Replace bespoke metadata schemas with a single shared vocabulary.",
  },
  {
    icon: Cloud,
    color: "#4051b5",
    title: "Multi-Cloud Integration",
    description:
      "Integrate data products across different cloud platforms and vendors with vendor-neutral descriptions. Portability is designed in, not retrofitted.",
  },
  {
    icon: Shield,
    color: "#ff6f00",
    title: "Data Governance & Compliance",
    description:
      "Track lineage, enforce policies, and maintain quality metrics across all data products. DPROD integrates with ODRL, PROV, and DQV for end-to-end governance.",
  },
];

export default function ConceptsPage() {
  return (
    <div className="flex flex-col">
      {/* Page header */}
      <section className="border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-20 md:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              Model
            </p>
            <h1 className="mb-6 text-4xl font-black tracking-tighter md:text-6xl">
              Core Concepts
            </h1>
            <p className="text-xl text-muted-foreground md:text-2xl">
              The building blocks of every DPROD description. Each concept
              links to its normative definition in the specification.
            </p>
          </div>
        </div>
      </section>

      {/* Concepts */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <div className="space-y-6">
              {CONCEPTS.map(
                ({ icon: Icon, color, title, description, anchor }) => (
                  <div
                    key={anchor}
                    className="rounded-xl border p-8 transition-colors hover:border-[#4051b5]/40"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:gap-6">
                      <Icon
                        className="h-12 w-12 shrink-0"
                        style={{ color }}
                      />
                      <div className="flex-1">
                        <h2 className="mb-2 text-2xl font-bold">{title}</h2>
                        <p className="mb-4 text-muted-foreground">
                          {description}
                        </p>
                        <Link
                          href={`/spec/#${anchor}`}
                          className="inline-flex items-center gap-1 font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                        >
                          Normative definition in the spec
                          <ArrowRight className="h-4 w-4" />
                        </Link>
                      </div>
                    </div>
                  </div>
                ),
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section>
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-4 text-3xl font-bold">Use cases</h2>
            <p className="mb-10 max-w-3xl text-lg text-muted-foreground">
              Where DPROD delivers its value. Each use case is reinforced by
              the same small vocabulary — no per-project extensions required.
            </p>
            <div className="grid gap-6 md:grid-cols-2">
              {USE_CASES.map(
                ({ icon: Icon, color, title, description }) => (
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
                ),
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
