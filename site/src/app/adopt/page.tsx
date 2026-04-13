import type { Metadata } from "next";
import Link from "next/link";
import {
  Rocket,
  Code2,
  Quote,
  FolderOpen,
  ExternalLink,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Adopt DPROD — Getting Started",
  description:
    "How to reference the Data Product Ontology in your own work: the JSON-LD @context, how to cite the OMG standard, and where to find worked examples.",
};

const JSONLD_SNIPPET = `{
  "@context": "https://www.omg.org/spec/DPROD/dprod-context.jsonld",
  "@type": "DataProduct",
  "id": "https://example.com/data-products/customer-360",
  "label": "Customer 360",
  "description": "A unified view of the customer across domains.",
  "outputPort": [
    {
      "@type": "DataService",
      "id": "https://example.com/data-products/customer-360/api"
    }
  ]
}`;

const CITATION = `Object Management Group (OMG). Data Product Ontology (DPROD), Version 1.0.
OMG Document Number: dtc/2024-09-01.
https://www.omg.org/spec/DPROD/`;

export default function AdoptPage() {
  return (
    <div className="flex flex-col">
      {/* Page header */}
      <section className="border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-20 md:py-28">
          <div className="mx-auto max-w-4xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              Adoption
            </p>
            <h1 className="mb-6 text-4xl font-black tracking-tighter md:text-6xl">
              Getting started
            </h1>
            <p className="text-xl text-muted-foreground md:text-2xl">
              Four concrete steps to start describing your data products with
              DPROD — from the JSON-LD context to the formal citation.
            </p>
          </div>
        </div>
      </section>

      {/* Steps */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-4xl space-y-16">
            {/* Step 1: JSON-LD */}
            <div>
              <div className="mb-4 flex items-center gap-3">
                <Code2 className="h-8 w-8 text-[#4051b5]" />
                <h2 className="text-2xl font-bold">
                  1. Reference the JSON-LD context
                </h2>
              </div>
              <p className="mb-6 text-muted-foreground">
                DPROD ships a stand-alone JSON-LD{" "}
                <code className="rounded bg-muted px-1.5 py-0.5 text-sm">
                  @context
                </code>{" "}
                so you can describe data products in plain JSON and get full
                RDF semantics for free. Point your documents at the published
                context URL:
              </p>
              <div className="overflow-x-auto rounded-lg border bg-muted/40 p-4">
                <pre className="text-sm">
                  <code>{JSONLD_SNIPPET}</code>
                </pre>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">
                Any JSON-LD processor will expand these terms into the full
                DPROD vocabulary automatically — no code generation, no schema
                compilation.
              </p>
            </div>

            {/* Step 2: Worked examples */}
            <div>
              <div className="mb-4 flex items-center gap-3">
                <FolderOpen className="h-8 w-8 text-[#ff6f00]" />
                <h2 className="text-2xl font-bold">
                  2. Study the worked examples
                </h2>
              </div>
              <p className="mb-6 text-muted-foreground">
                The specification includes worked examples covering common
                patterns: SBA pool rates, equity trades, core data product
                extensions, data lineage, data quality, data rights, data
                schemas, and observability ports. Each example is a complete,
                machine-readable JSON-LD file you can copy and adapt.
              </p>
              <Button asChild variant="outline">
                <a
                  href="https://github.com/EKGF/dprod/tree/develop/examples"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Browse examples on GitHub
                </a>
              </Button>
            </div>

            {/* Step 3: Validate */}
            <div>
              <div className="mb-4 flex items-center gap-3">
                <Rocket className="h-8 w-8 text-[#4051b5]" />
                <h2 className="text-2xl font-bold">
                  3. Validate with the SHACL shapes
                </h2>
              </div>
              <p className="mb-6 text-muted-foreground">
                DPROD ships SHACL shapes that any conforming RDF tool can use
                to validate your data product descriptions. If a description
                passes the shapes, it conforms to the standard — full stop.
                There is nothing extra to implement.
              </p>
              <div className="flex flex-wrap gap-3">
                <Button asChild variant="outline">
                  <Link href="/spec/">
                    <ArrowRight className="mr-2 h-4 w-4" />
                    Browse the shapes in the spec
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <a
                    href="https://github.com/EKGF/dprod/blob/develop/ontology/dprod/dprod-shapes.ttl"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Raw SHACL file
                  </a>
                </Button>
              </div>
            </div>

            {/* Step 4: Cite */}
            <div>
              <div className="mb-4 flex items-center gap-3">
                <Quote className="h-8 w-8 text-[#ff6f00]" />
                <h2 className="text-2xl font-bold">
                  4. Cite the OMG standard
                </h2>
              </div>
              <p className="mb-6 text-muted-foreground">
                When you reference DPROD in papers, internal documentation, or
                procurement requirements, use the formal OMG citation:
              </p>
              <div className="overflow-x-auto rounded-lg border bg-muted/40 p-4">
                <pre className="text-sm whitespace-pre-wrap">
                  <code>{CITATION}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Resources */}
      <section>
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-10 text-3xl font-bold">Go deeper</h2>
            <div className="grid gap-6 md:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle>The specification</CardTitle>
                  <CardDescription className="mt-2 text-base">
                    The complete, normative DPROD specification with classes,
                    properties, and shapes.
                  </CardDescription>
                  <div className="mt-4">
                    <Link
                      href="/spec/"
                      className="inline-flex items-center gap-1 text-sm font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Open the spec
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Core concepts</CardTitle>
                  <CardDescription className="mt-2 text-base">
                    A plain-English walkthrough of Data Products, Ports,
                    Distributions, and Datasets.
                  </CardDescription>
                  <div className="mt-4">
                    <Link
                      href="/concepts"
                      className="inline-flex items-center gap-1 text-sm font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Read concepts
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Contact the working group</CardTitle>
                  <CardDescription className="mt-2 text-base">
                    Questions, feedback, or interested in contributing? Reach
                    out to the EKGF community.
                  </CardDescription>
                  <div className="mt-4">
                    <Link
                      href="/contact"
                      className="inline-flex items-center gap-1 text-sm font-medium text-[#4051b5] transition-colors hover:text-[#5c6bc0]"
                    >
                      Get in touch
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
