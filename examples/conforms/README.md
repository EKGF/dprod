The Data Product provides to the consumers (dprod:outputDataset) datasets defined based on [DCAT](https://www.w3.org/TR/vocab-dcat-3/).
Datasets should be described ([dcat:conforms](https://www.w3.org/TR/vocab-dcat-2/#Property:resource_conforms_to)) with logical models. 
Logical models describe business entities and their properties (attributes and relationships) with consistent business terms and they are technology independent.
Ideally, logical models are based on existing standards eg, [FIBO](https://spec.edmcouncil.org/fibo/ontology), [CDM](https://www.finos.org/common-domain-model) etc.
If a logical model does not exist to describe the dataset, then the dataset publisher can create one, preferably by using SHACL modelling language:

Example of a Dataset conforming to a SHACL Schema

~~~ exampleDataset dcat:conforms exampleSchema:DatasetLogicalSchema.
exampleSchema:DatasetLogicalSchema a owl:Ontology, dct:Standard.
~~~


Based on [SHACL](https://www.w3.org/TR/shacl/) all entities that exist in the dataset are Node Shapes (1).
The attributes of the entities are described as Property Shapes with sh:datatype (2)
The relationships are also defined as Property Shaped with sh:class the target class of the relationship  (3)


~~~
example:Account a sh:NodeShape;       // definition of the entity as a Node Shape (1)
rdfs:label "Account"@en;              // human readable name of the entity
dc:description "An Account is...";    // description of the entity
sh:property example:Account-AccountAge;       // an account has a property shape Account Age. Definition of the property shape follows (2)
sh:property example:Account-AccountBranch     // an account has a property shape Account Branch. Definition of the property shape follows   (3)
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Account-AccountAge a sh:PropertyPage;   // (2) Definition of the Account-AccountAge property shape describing that an account MUST have exactly AccountAge attribute and its datatype is integer
sh:path example:AccountAge;
sh:datatype xsd:integer;
sh:minCount 1;
sh:maxCount 1;
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Account-AccountBranch a sh:PropertyPage;   // (3) Definition of the Account-AccountBranch property shape describing than an account must have at least one Account Branch which is another entity
sh:path example:AccountBranch;
sh:class  example:Branch;
sh:minCount 1;
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Branch a sh:NodeShape;     //definition of the entity Branch as a Node Shape (1)
rdfs:label "Branch"@en;              // human readable description of the entity
dc:description "A Branch is..";
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
....
~~~
