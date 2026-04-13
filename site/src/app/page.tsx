import Link from "next/link";
import {
  Network,
  FileJson,
  GitBranch,
  Shield,
  ExternalLink,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden border-b bg-linear-to-br from-[#4051b5]/8 via-background to-background">
        <div className="container py-24 md:py-36">
          <div className="mx-auto max-w-4xl text-center">
            <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#4051b5]">
              OMG Standard
            </p>
            <h1 className="mb-6 text-5xl font-black tracking-tighter md:text-7xl">
              Data Product Ontology
            </h1>
            <p className="mb-10 text-xl text-muted-foreground md:text-2xl">
              An OMG standard for describing Data Products using W3C Linked Data
              technologies, enabling interoperability and discoverability in
              decentralized data ecosystems
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button asChild size="lg" className="bg-[#4051b5] text-white hover:bg-[#303f9f]">
                <Link href="/spec-versions">View Specification</Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link href="/adopt">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* What is DPROD */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-4xl">
            <div className="rounded-xl border p-8 bg-linear-to-br from-[#4051b5]/5 to-[#303f9f]/5">
              <h2 className="mb-4 text-2xl font-bold">What is DPROD?</h2>
              <p className="mb-4 text-lg leading-relaxed">
                The Data Product Ontology (DPROD) is an{" "}
                <a
                  href="https://www.omg.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold text-[#4051b5] hover:text-[#5c6bc0] transition-colors"
                >
                  Object Management Group (OMG)
                </a>{" "}
                standard that profiles the W3C Data Catalog Vocabulary (DCAT) to
                specifically describe Data Products. As organizations increasingly
                adopt decentralized data architectures like Data Mesh, DPROD
                provides the standardization needed to ensure interoperability and
                unlock the full potential of distributed data ecosystems.
              </p>
              <p className="text-lg leading-relaxed">
                Built on established W3C technologies including DCAT, RDF, OWL,
                SHACL, and PROV, DPROD offers a clear schema for describing data
                products, ensuring they are discoverable, interoperable, and
                treated with the same level of accountability as traditional
                products.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Key Benefits */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-5xl">
            <h2 className="mb-10 text-3xl font-bold text-center">Key Benefits</h2>
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <Network className="h-10 w-10 text-[#4051b5] mb-2" />
                  <CardTitle>Decentralized Architecture</CardTitle>
                  <CardDescription className="text-base mt-2">
                    Enable Data Mesh and other decentralized data architectures by
                    providing standard methods to describe data products
                    consistently across platforms and domains.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <FileJson className="h-10 w-10 text-[#ff6f00] mb-2" />
                  <CardTitle>Standardized Metadata</CardTitle>
                  <CardDescription className="text-base mt-2">
                    Eliminate inconsistent metadata across data products with an
                    OMG standard framework that leverages W3C technologies for
                    machine-readable descriptions.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <GitBranch className="h-10 w-10 text-[#4051b5] mb-2" />
                  <CardTitle>Input &amp; Output Ports</CardTitle>
                  <CardDescription className="text-base mt-2">
                    Clearly define how data enters and leaves data products through
                    standardized input and output ports, supporting various formats
                    and protocols.
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <Shield className="h-10 w-10 text-[#ff6f00] mb-2" />
                  <CardTitle>Data Governance</CardTitle>
                  <CardDescription className="text-base mt-2">
                    Integrate with ODRL for rights management, PROV for lineage,
                    and DQV for quality metrics, ensuring comprehensive data
                    governance.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Articles & Talks */}
      <section className="border-b">
        <div className="container py-20">
          <div className="mx-auto max-w-4xl">
            <h2 className="mb-8 text-3xl font-bold">Articles &amp; Talks</h2>
            <div className="space-y-4">
              {[
                {
                  color: "#4051b5",
                  title: "Tony Seale: Data Products & Ontologies (DPROD)",
                  description:
                    `A practical introduction to DPROD as a "first step" towards a distributed knowledge graph—covering JSON-LD contexts, linkable product identifiers, and connecting outputs to shared semantic schemas.`,
                  linkHref:
                    "https://www.knowledge-graph-guys.com/blog/data-products-ontologies",
                  linkLabel: "Read the article",
                },
                {
                  color: "#ff6f00",
                  title: "OMG announcement: DPROD published for public comment",
                  description:
                    "The official OMG news release explains the motivation for DPROD, the Request for Comments process, and the problems it targets (inconsistent metadata, limited discoverability, and interoperability).",
                  linkHref:
                    "https://www.omg.org/news/releases/pr2024/09-24-24.htm",
                  linkLabel: "Read the OMG release",
                },
                {
                  color: "#4051b5",
                  title:
                    "Workshop video: AI agents with reusable Data Products (DPROD)",
                  description:
                    "A practical session on building reusable semantic data products with DPROD and connecting them into a decentralized knowledge graph for AI/agent use cases.",
                  linkHref:
                    "https://watch.knowledgegraph.tech/videos/day-2-classroom-225-build-your-neuro-symbolic-ai-agent-720p",
                  linkLabel: "Watch the video",
                },
                {
                  color: "#ff6f00",
                  title:
                    `agnos.ai: Beyond Data Mesh—how Virtual Knowledge Graphs prevent "Data Mess"`,
                  description:
                    `A perspective on why "data products" alone are not enough—without a semantic foundation, decentralized ownership tends to create fragmentation. Links Data Mesh concepts to operational knowledge graphs and governance.`,
                  linkHref: "https://agnos.ai/insights/article/beyond-data-mesh",
                  linkLabel: "Read the article",
                },
                {
                  color: "#4051b5",
                  title:
                    "Podcast: Knowledge-first Data Products & the Data Economy (Jacobus Geluk)",
                  description:
                    "A discussion of use case-driven approaches and semantic coordination as foundations for scalable data product marketplaces—useful context for why standards like DPROD matter.",
                  linkHref:
                    "https://agnos.ai/insights/podcast/knowledge-graph-data-economy",
                  linkLabel: "Open the podcast page",
                },
                {
                  color: "#4051b5",
                  title: "Ontologies & LLMs (Tony Seale)",
                  description:
                    "Background reading on why formal semantics matter for AI—and why linking data products to shared concepts helps make data more machine-understandable.",
                  linkHref:
                    "https://hyperight.com/beyond-the-hype-how-ontologies-unlock-the-potential-of-large-language-models-tony-seale-the-knowledge-graph-guy/",
                  linkLabel: "Read the article",
                },
              ].map(({ color, title, description, linkHref, linkLabel }) => (
                <div key={linkHref} className="rounded-lg border p-6">
                  <div className="flex items-start gap-4">
                    <BookOpen
                      className="mt-1 h-6 w-6 shrink-0"
                      style={{ color }}
                    />
                    <div className="space-y-2">
                      <h3 className="text-xl font-semibold">{title}</h3>
                      <p className="text-muted-foreground">{description}</p>
                      <a
                        href={linkHref}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center font-medium text-[#4051b5] hover:text-[#5c6bc0] transition-colors"
                      >
                        {linkLabel}{" "}
                        <ExternalLink className="ml-2 h-4 w-4" />
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA strip */}
      <section className="container py-20">
        <div className="mx-auto max-w-4xl">
          <Card className="bg-linear-to-br from-[#4051b5] to-[#303f9f] text-white border-0">
            <CardHeader>
              <CardTitle className="text-2xl text-white mb-2">
                OMG Standard with W3C Technologies
              </CardTitle>
              <CardDescription className="text-white/90 text-base">
                DPROD is an OMG standard built on established W3C technologies
                including DCAT, RDF, OWL, SHACL, and PROV. The specification
                includes:
              </CardDescription>
              <ul className="mt-4 space-y-2 text-white/90 text-sm">
                <li className="flex items-start gap-2">
                  <span aria-hidden>•</span>
                  <span>Complete ontology with classes and properties</span>
                </li>
                <li className="flex items-start gap-2">
                  <span aria-hidden>•</span>
                  <span>SHACL shapes for validation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span aria-hidden>•</span>
                  <span>JSON-LD context for easy JSON integration</span>
                </li>
                <li className="flex items-start gap-2">
                  <span aria-hidden>•</span>
                  <span>Worked examples and best practices</span>
                </li>
              </ul>
              <div className="mt-6 flex flex-wrap gap-4">
                <Button
                  asChild
                  variant="secondary"
                  size="lg"
                  className="bg-white text-[#4051b5] hover:bg-white/90"
                >
                  <Link href="/spec-versions">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    View Specification
                  </Link>
                </Button>
                <Button
                  asChild
                  variant="secondary"
                  size="lg"
                  className="bg-white/90 text-[#4051b5] hover:bg-white"
                >
                  <a
                    href="https://www.omg.org/news/releases/pr2024/09-24-24.htm"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <ExternalLink className="mr-2 h-4 w-4" />
                    OMG Public Comment Notice
                  </a>
                </Button>
                <Button
                  asChild
                  variant="outline"
                  size="lg"
                  className="bg-transparent border-white text-white hover:bg-white/10"
                >
                  <a
                    href="https://github.com/EKGF/dprod"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    GitHub Repository
                  </a>
                </Button>
              </div>
            </CardHeader>
          </Card>
        </div>
      </section>
    </div>
  );
}
