# Concepts

## Data mesh concepts

### Data Product
It's the smallest unit that can be independently deployed and managed in a data architecture (i.e. architectural quantum). It is composed of all the structural components that it requires to do its function: the metadata, the data, the code, the policies that govern the data and its dependencies on infrastructure. Each data product has a clear identifier, a version number and an owner.

Aside from general information, a data product is composed of external interfaces (i.e. interface components) and internal resources (i.e. internal components). Interface components are public and are used by external agents to access services exposed by the data product. Internal components are private and are used by the underlying DataOps Platform to deploy and operate the data product.


### Data Product's Interface Components
The interfaces are exposed to external agents by a data product. These interfaces are grouped by functional role in entities named ports. Each port exposes a service or set of correlated services. These are the five types of ports supported by the DPSD:

- **Input port(s):** an input port describes a set of services exposed by a data product to collect its source data and makes it available for further internal transformation. An input port can receive data from one or more upstream sources in a push (i.e. asynchronous subscription) or pop mode (i.e. synchronous query). Each data product may have one or more input ports.
- **Output port(s):** an output port describes a set of services exposed by a data product to share the generated data in a way that can be understood and trusted. Each data product may have one or more output ports.
- **Discovery port(s):** a discovery port describes a set of services exposed by a data product to provide information about its static role in the overall architecture like purpose, structure, location, etc. Each data product may have one or multiple discovery ports.
- **Observability port(s):** an observability port describes a set of services exposed by a data product to provide information about its dynamic behavior in the overall architecture like logs, traces, audit trails, metrics, etc. Each data product may have one or more observability ports.
- **Control port(s):** a control port describes a set of services exposed by a data product to configure local policies or perform highly privileged governance operations. Each data product may have one or more control ports.


### Data Product's Internal Components

*TODO*

- **Application Components:** The components of a data product that implement the services exposed through its ports (i.e. pipelines, microservices, etc..).
- **Infrastructural Components**
The components of a data product related to the infrastructural resources (i.e. storage, computing, etc..) used to run its application components.

## Data product descriptor specification (DPDS)

It's the document that serves as an entry to all the information about a data product, including its fully qualified name, owner, domain, version, interface components and internal components. It is used to share a complete view of the data product between consumers and the underlying DataOps Platform throughout its lifecycle. The objective of DPDS is to provide a standard to define the structure and content of this document.

Immagine

A noi interessa solo la parte relativa alle genaeral info e alle interfacce.

Immagine

### DPDS General Info
*TODO*

### DPDS Port
*TODO*

### DPDS Port's API
*TODO*


## Data Catalog Vocabulary (DCAT)


## DPDS and DCAT mapping

Possibili mapping tra concetti:

**Data Product = Resource**

**Data Product = Dataset**

**Data Product = Catalog**


