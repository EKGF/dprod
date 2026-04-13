import type { Metadata } from "next";
import { Roboto, Roboto_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

const roboto = Roboto({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  variable: "--font-roboto",
  display: "swap",
});

const robotoMono = Roboto_Mono({
  subsets: ["latin"],
  variable: "--font-roboto-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DPROD — Data Product Ontology",
  description:
    "An OMG standard for describing Data Products using W3C Linked Data technologies, enabling interoperability and discoverability in decentralized data ecosystems.",
  keywords: [
    "Data Product",
    "Data Mesh",
    "DPROD",
    "Ontology",
    "OWL",
    "SHACL",
    "DCAT",
    "EKGF",
    "OMG",
  ],
  authors: [
    {
      name: "Object Management Group (OMG) Enterprise Knowledge Graph Forum",
    },
  ],
  openGraph: {
    title: "DPROD — Data Product Ontology",
    description:
      "An OMG standard for describing Data Products using W3C Linked Data technologies.",
    siteName: "DPROD",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var m=document.cookie.match(/(^|;\\s*)ekgf-theme=([^;]*)/);var t=m?decodeURIComponent(m[2]):"";if(t==="dark"||t==="light"){try{localStorage.setItem("theme",t)}catch(e){};if(t==="dark"){document.documentElement.classList.add("dark");document.documentElement.classList.remove("light");}else{document.documentElement.classList.add("light");document.documentElement.classList.remove("dark");}}}catch(e){}})();`,
          }}
        />
      </head>
      <body className={`${roboto.variable} ${robotoMono.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
