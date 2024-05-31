The Data Product outputs datasets which are defined with DCAT.
Datasets are described ( __dcat:conforms__) with logical models. 
Logical models are consistent business models, technology independent
Ideally, logical models are ideally based on existing standards eg, FIBO, CDM etc

If a logical schema does not exist to describe the dataset then the dataset publisher can create one preferably by using SHACL modelling language

exampleDataset dcat:conforms exampleSchema:DatasetLogicalSchema.
exampleSchema:DatasetLogicalSchema a owl:Ontology.


Based on SHACL all entities that exist in the dataset are Node Shapes.
The attributes of the entities are described as Property Shapes with sh:datatype an xsd datatype
The relationships are also defined as Property Shaped with sh:class the target class of the relationship


example:Account a sh:NodeShape;       // definition of the entity as a Node Shape
rdfs:label "Account"@en;              // human readable description of the entity
sh:property example:Account-AccountAge;       // an account has a property shape Account Age. Definition of the property shape follows 
sh:property example:Account-AccountBranch     // an account has a property shape Account Branch. Definition of the property shape follows 
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Account-AccountAge a sh:PropertyPage;   // Definition of the Account-AccountAge property shape describing that an account MUST have exactly AccountAge attribute and its datatype is integer
sh:path example:AccountAge;
sh:datatype xsd:integer;
sh:minCount 1;
sh:maxCount 1;
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Account-AccountBranch a sh:PropertyPage;   // Definition of the Account-AccountBranch property shape describing than an account must have at least one Account Branch which is another entity
sh:path example:AccountBranch;
sh:class  example:Branch;
sh:minCount 1;
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
.

example:Branch a sh:NodeShape;       // definition of the entity Branch as a Node Shape
rdfs:label "Branch"@en;              // human readable description of the entity
rdfs:isDefinedBy exampleSchema:DatasetLogicalSchema;
....
