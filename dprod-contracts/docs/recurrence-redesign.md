I would suggest you change the prod:recurrence to work - basically - like it does in DCAT. Point to an individual that carries the conformsTo identifier and the spec itself. 



  1. New class — add after dprod:RuntimeReference                                                                                                                                                                                                                  

                                                                                                                                                                                                                                                                                  

  dprod:RecurrenceSpec                                                                                                                                                                                                                                                            

    a owl:Class ;                                                                                                                                                                                                                                                                 

    dct:description "A recurrence specification in a named grammar or controlled vocabulary."@en ;                                                                                                                                                                              

    rdfs:comment                                                                                                                                                                                                                                                                  

      """Two usage patterns:

      Expression-based (iCal RRULE, crontab, etc.):                                                                                                                                                                                                                               

        dprod:recurrence [

          a dprod:RecurrenceSpec ;                                                                                                                                                                                                                                                

          dct:conformsTo dprod:RuleScheme ;                                                                                                                                                                                                                                    

          rdf:value "FREQ=DAILY;BYHOUR=6;BYMINUTE=0"                                                                                                                                                                                                                              

        ] .

                                                                                                                                                                                                                                                                                  

      Vocabulary-based (DCAT frequency URI):                                                                                                                                                                                                                                    

        dprod:recurrence <http://purl.org/cld/freq/daily> .

                                                                                                                                                                                                                                                                                  

      For vocabulary-based use, the named URI individual is implicitly a                                                                                                                                                                                                          

      RecurrenceSpec; no blank node is required.                                                                                                                                                                                                                                  

      New grammars can be defined by third parties via dct:conformsTo."""@en ;                                                                                                                                                                                                    

    rdfs:isDefinedBy <https://www.omg.org/spec/DPROD/contracts/> ;                                                                                                                                                                                                                  

    rdfs:label "recurrence spec" ;

  .                                                                                                                                                                                                                                                                               

                                                                                                                                                                                                                                                                                

  ---                                                                                                                                                                                                                                                                             

  2. New named individuals - examples - pick or extend as you like — add after the class above                                                                                                                                                                                                                          

                                                                                                                                                                                                                                                                                  

  dprod:RRuleScheme

    a dprod:RecurrenceSpec ;                                                                                                                                                                                                                                                      

    dct:description "RFC 5545 iCalendar RRULE grammar."@en ;                                                                                                                                                                                                                    

    rdfs:isDefinedBy <https://www.omg.org/spec/DPROD/contracts/> ;                                                                                                                                                                                                                  

    rdfs:label "RRule scheme" ;

    rdfs:seeAlso <https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10> ;                                                                                                                                                                                                        

  .                                                                                                                                                                                                                                                                               

                                                                                                                                                                                                                                                                                  

  dprod:CrontabScheme                                                                                                                                                                                                                                                             

    a dprod:RecurrenceSpec ;                                                                                                                                                                                                                                                    

    dct:description "Unix crontab expression grammar (minute hour dom month dow)."@en ;

    rdfs:isDefinedBy <https://www.omg.org/spec/DPROD/contracts/> ;                                                                                                                                                                                                                  

    rdfs:label "crontab scheme" ;                                                                                                                                                                                                                                                 

    rdfs:seeAlso <https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html> ;                                                                                                                                                                                      

  .                                                                                                                                                                                                                                                                               

                                                                                                                                                                                                                                                                                

  ---                                                                                                                                                                                                                                                                             

  3. Replace dprod:recurrence                                                                                                                                                                                                                               

                                             

  Remove:

  dprod:recurrence                                                                                                                                                                                                                                                                

    a owl:DatatypeProperty ;

    dct:description "RFC 5545 RRULE defining when duty instances are generated."@en ;                                                                                                                                                                                             

    rdfs:comment                                                                                                                                                                                                                                                                

      """An RFC 5545 RRULE string (e.g., FREQ=DAILY;BYHOUR=6;BYMINUTE=0).

      Defines the schedule on which duty instances are created.          

      Each instance follows the standard duty lifecycle independently.                                                                                                                                                                                                            

      The deadline property defines the per-instance fulfillment window.

      Any iCal-compliant library can parse the value."""@en ;                                                                                                                                                                                                                     

    rdfs:isDefinedBy <https://www.omg.org/spec/DPROD/contracts/> ;                                                                                                                                                                                                                  

    rdfs:domain odrl:Duty ;                                     

    rdfs:range xsd:string ;                                                                                                                                                                                                                                                       

    rdfs:label "recurrence" ;                                                                                                                                                                                                                                                     

  .

                                                                                                                                                                                                                                                                                  

  Replace with:                                                                                                                                                                                                                                                                 

  dprod:recurrence

    a owl:ObjectProperty ;

    dct:description "Schedule on which duty instances are generated."@en ;

    rdfs:comment                                                                                                                                                                                                                                                                  

      """Value is a dprod:RecurrenceSpec — either a structured blank node

      (expression-based grammars) or a named frequency URI (vocabulary-based).                                                                                                                                                                                                    

                                                                                                                                                                                                                                                                                  

      Expression-based — pair dct:conformsTo with rdf:value:                                                                                                                                                                                                                      

        dprod:recurrence [                                                                                                                                                                                                                                                        

          a dprod:RecurrenceSpec ;                                                                                                                                                                                                                                                

          dct:conformsTo dprod:RRuleScheme ;                                                                                                                                                                                                                                      

          rdf:value "FREQ=DAILY;BYHOUR=6;BYMINUTE=0"

        ] .                                                                                                                                                                                                                                                                       

        dprod:recurrence [                                                                                                                                                                                                                                                      

          a dprod:RecurrenceSpec ;                                                                                                                                                                                                                                                

          dct:conformsTo dprod:CrontabScheme ;

          rdf:value "0 6 * * *"                                                                                                                                                                                                                                                   

        ] .                                                                                                                                                                                                                                                                     

                                                                                                                                                                                                                                                                                  

      Vocabulary-based (e.g. DCAT Dublin Core frequency URIs):

        dprod:recurrence <http://purl.org/cld/freq/daily> .                                                                                                                                                                                                                       

                                                                                                                                                                                                                                                                                

      Each duty instance follows the standard lifecycle independently.                                                                                                                                                                                                            

      The deadline property defines the per-instance fulfillment window.

      New grammars can be introduced by defining a new dprod:RecurrenceSpec                                                                                                                                                                                                       

      individual and using it as the dct:conformsTo value."""@en ;                                                                                                                                                                                                              

    rdfs:isDefinedBy <https://www.omg.org/spec/DPROD/contracts/> ;                                                                                                                                                                                                                  

    rdfs:domain odrl:Duty ;                                                                                                                                                                                                                                                       

    rdfs:range dprod:RecurrenceSpec ;                                                                                                                                                                                                                                             

    rdfs:label "recurrence" ;                                                                                                                                                                                                                                                     

  .                                                                                                                                                                                                                                                                             

                                                                                                                                                                                                                                                                                  

  ---                                                                                                                                                                                                                                                                           

  Also update the ontology header description (line 34)

                                                                                                                                                                                                                                                                                  

  Remove:

      - Recurrence property on odrl:Duty (RFC 5545 RRULE)                                                                                                                                                                                                                         

  Replace with:                                                                                                                                                                                                                                                                 

      - Recurrence property on odrl:Duty (iCal RRULE, crontab, or frequency URI)                                                                                                                                                                                                  

     

  ---                                                                                                                                                                                                                                                                             

  Summary of what changes                                                                                                                                                               
