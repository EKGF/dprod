# Concepts

## Data mesh concepts

### Data Product
It's the smallest unit that can be independently deployed and managed in a data architecture (i.e. architectural quantum). It is composed of all the structural components that it requires to do its function: the metadata, the data, the code, the policies that govern the data and its dependencies on infrastructure. Each data product has a clear identifier, a version number and an owner.

Aside from general information, a data product is composed of external interfaces (i.e. interface components) and internal resources (i.e. internal components). Interface components are public and are used by external agents to access services exposed by the data product. Internal components are private and are used by the underlying DataOps Platform to deploy and operate the data product.

Note: In data mesh a data product is not just a dataset or collection of datasets. It can be seen as a microservice whose primary objective is to provide access to data rather than business functions.


### Data Product's Interface Components
External consumers interact with a data product through its public interfaces. These interfaces are grouped by functional role in entities named ports. Each port exposes a service or set of correlated services. These are the five types of ports usially exposed by a data product:

- **Input port(s):** an input port describes a set of services exposed by a data product to collect its source data and makes it available for further internal transformation. An input port can receive data from one or more upstream sources in a push (i.e. asynchronous subscription) or pop mode (i.e. synchronous query). Each data product may have one or more input ports.
- **Output port(s):** an output port describes a set of services exposed by a data product to share the generated data in a way that can be understood and trusted. Each data product may have one or more output ports.
- **Discovery port(s):** a discovery port describes a set of services exposed by a data product to provide information about its static role in the overall architecture like purpose, structure, location, etc. Each data product may have one or multiple discovery ports.
- **Observability port(s):** an observability port describes a set of services exposed by a data product to provide information about its dynamic behavior in the overall architecture like logs, traces, audit trails, metrics, etc. Each data product may have one or more observability ports.
- **Control port(s):** a control port describes a set of services exposed by a data product to configure local policies or perform highly privileged governance operations. Each data product may have one or more control ports.


### Data Product's Internal Components

A data product consists of the following internal components:

- **Application Components:** The components of a data product that implement the services exposed through its ports (i.e. pipelines, microservices, etc..).
- **Infrastructural Components**
The components of a data product related to the infrastructural resources (i.e. storage, computing, etc..) used to run its application components.

These components are not visible to its consumers. They are used by the underlying platform to automate the data producs lifecycle from cretaion to retirement.

## Data product descriptor specification (DPDS)

It's the document that serves as an entry to all the information about a data product, including its fully qualified name, owner, domain, version, interface components and internal components. It is used to share a complete view of the data product between consumers and the underlying DataOps Platform throughout its lifecycle. The objective of DPDS is to provide a standard to define the structure and content of this document.

[Immagine]

For the time being, the activities of the working group are focused on the publicly visible part of the data product (general info and interfaces). Therefore, we will not delve further into the structure and content of the sections of the DPDS that describe the internal components.

[Immagine]

### DPDS General Info

General info can be used to provide a high level descriptiono of the data product. Common properties of this configuration block are:

	- `fullyQualifiedName` (**string:fqn**): This is the unique universal identifier of the data product.  It MUST be a URN of the form `urn:dpds:{mesh-namespace}:dataproducts:{product-name}:{product-major-version}`. It's RECOMMENDED to use as `mesh-namespace` your company's domain name in reverse dot notation (ex. `com.company-xyz`) in order to ensure that the `fullyQualifiedName` is a unique universal idetifier as REQUIRED.
	- `version` (**string:version**): this is the <a href="https://semver.org/spec/v2.0.0.html" target="_blank">semantic version number</a> of the data product (not to be confused with the `dataProductDescriptor` version above).
	- `domain` (**string**): This is the domain to which the data product belongs.
	- `owner` ([Owner Object](../resources/specifications/last.md#owner-object)): This is a collection of information related to the data product's owner. The only mandatory field is the `id` of the owner, usually his or her corporate mail address.
  
NOTE: General info does not contains en explicit definition of the dataset served by the data product. *TODO*


### DPDS Port
All ports, regardless of their type, are described using the following fields:

- `fullyQualifiedName` (**string:fqn**): The unique universal identifier of the port. It MUST be a URN of the form `urn:dpds:{mesh-namespace}:dataproducts:{product-name}:{product-major-version}:{port-type}:{port-name}`
- `version`: (**string:version**): This is the <a href="https://semver.org/spec/v2.0.0.html" target="_blank">semantic version number</a> of the data product's port. Every time the *major version* of port changes also the *major version* of the product MUST be incremented.
- `promises` ([Promises Object](../resources/specifications/last.md#promises-object)): These are the data product's [promises](../concepts/data-contract.md) declared over the port.  Through promises the data product declares the intent of the port. Promises are not a guarantee of the outcome but the data product will behave accordingly to them to realize its intent. The more a data product keeps its promises over time and the more trustworthy it is. Thus, the more trustworthy a data product is the more potential consumers are likely to use it. Trust is based on the verification of how good a data product was in the past in keeping its promises. This verification should be automated by the underlying platform and synthesized in a trust score shared with all potential consumers. Examples of promises are descriptions of services' API, SLO, deprecation policy, etc.
- `expectations` ([Expectations Object](../resources/specifications/last.md#expectations-object)): These are the data product's [expectations](../concepts/data-contract.md) declared over the port. Through expectations the data product declares how it wants the port to be used by its consumers. Expectations are the inverse of promises. They are a way to explicitly state what promises the data product would like consumers to make regarding how they will use the port. Examples of expectations are intended usage, intended audience, etc.
- `contracts` ([Contracts Object](../resources/specifications/last.md#contracts-object)): These are the data product's [contracts](../concepts/data-contract.md) declared over the port. Through contracts the data product declares promises and expectations that must be respected both by itself and its consumers respectively. A contract is an explicit agreement between the data product and its consumers. It is used to group all the promises and expectations that if not respected can generate penalties like monetary sanctions or interruption of service. Examples of contracts are terms of conditions, SLA, billing policy, etc.

A data product can have multiple ports of the same type, for example it is possible to have multiple output ports and/or inpunt ports.

### DPDS Port's API
The API of a port is part of its promises. The promises configuration block composed by the following fields:

- `platform` (**string**): This is the target technological platform in which the services associated with the given port operate. Examples: `onprem:milan-1`, `aws:eu-south-1`, `aws:eu-south-1:redshift`.
- `servicesType` (**string**): This is the type of service associated with the given port. Examples: `soap-services`, `rest-services`, `odata-services`,`streaming-services`, `datastore-services`.
- `api` ([Standard Definition Object](../resources/specifications/last.md#standardDefinitionObject)): this is the formal description of services API. A good API standard specification should describe how to define the following elements of the service interface: addressable endpoints, available authentication methods and schema of data object exchanged.
	- `specification` (**string**): This is the name of the specification used to define the service API. It is RECOMMENDED to use [Open API Specification](https://github.com/OAI/OpenAPI-Specification) for restful services, [Async API Specification](https://github.com/asyncapi/spec) for streaming services and *DataStore API Specification* for data store connection-based services. Other specifications MAY be used as required.
	- `version` (**string**): This is the version of the specification used to define the service API.
	- `definition` (**Object**): This is the definition of the service API built using the specification reported in the fields above
- `depreceationPolicy` ([Specification Extension Point](../resources/specifications/last.md#specificationExtensionPoint)): This is the deprecation policy adopted for the given set of services. A policy description and a pointer to external documentation can be provided. Moreover, other fields with **"x-" prefix** can be added to provide further informations as needed (ex. `x-deprecation-period`).
	- `description` (**string**): This is a general description of the deprecation policy.
	- `externalDocs` ([External Resource Object](../resources/specifications/last.md#externalResourceObject)): This is a pointer to external documentation that describe in more detail the deprecation policy.
- `slo`: ([Specification Extension Point](../resources/specifications/last.md#specificationExtensionPoint)): These are the _service_ level objectives (SLO)* supported by the given set of services. An SLO description and a pointer to external documentation can be provided. Moreover, other fields with **"x-" prefix** can be added to provide further information as needed (ex. `x-availability`, `x-responsetime`, etc...).
	- `description` (**string**): This is a general description of the supported SLO
	- `externalDocs` ([External Resource Object](../resources/specifications/last.md#externalResourceObject)): This is a pointer to external documentation that describes in more detail the supported SLO.

NOTE: about schema *TODO*

## Data Catalog Vocabulary (DCAT)


## DPDS and DCAT mapping

Possibili mapping tra concetti:

**Data Product = Resource**

**Data Product = Dataset**

**Data Product = Catalog**


