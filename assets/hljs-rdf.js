/*
 * highlight.js grammars for Turtle and SPARQL, loaded into ReSpec's
 * highlighting worker by the preProcess hook in respec/template.html.
 * ReSpec bundles only abnf, css, http, javascript, json, xml and yaml.
 *
 * The worker runs `importScripts(langURL)` and then
 * `hljs.registerLanguage(lang, self[propName])`, so each grammar is exposed
 * as a global function.
 */
(function () {
  function rdfModes(hljs) {
    return {
      iri: { className: "link", begin: /<[^<>"{}|^`\\\s]*>/ },
      prefixedName: {
        className: "symbol",
        begin: /(?:[A-Za-z][\w.-]*)?:(?:[\w%-](?:[\w.%-]*[\w%-])?)?/,
      },
      blankNode: { className: "variable", begin: /_:[\w-]+/ },
      strings: [
        { className: "string", begin: /"""/, end: /"""/, contains: [hljs.BACKSLASH_ESCAPE] },
        { className: "string", begin: /'''/, end: /'''/, contains: [hljs.BACKSLASH_ESCAPE] },
        { className: "string", begin: /"/, end: /"/, illegal: /\n/, contains: [hljs.BACKSLASH_ESCAPE] },
        { className: "string", begin: /'/, end: /'/, illegal: /\n/, contains: [hljs.BACKSLASH_ESCAPE] },
      ],
      languageTag: { className: "meta", begin: /@[a-zA-Z]+(?:-[a-zA-Z0-9]+)*/ },
      number: { className: "number", begin: /[+-]?(?:\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)\b/ },
      comment: hljs.COMMENT(/#/, /$/),
    };
  }

  self.hljsDefineTurtle = function (hljs) {
    const m = rdfModes(hljs);
    return {
      name: "Turtle",
      aliases: ["ttl"],
      keywords: { keyword: "a PREFIX BASE prefix base", literal: "true false" },
      contains: [
        m.comment,
        m.iri,
        { className: "keyword", begin: /@(?:prefix|base)\b/ },
        ...m.strings,
        m.languageTag,
        m.blankNode,
        m.prefixedName,
        m.number,
      ],
    };
  };

  self.hljsDefineSparql = function (hljs) {
    const m = rdfModes(hljs);
    return {
      name: "SPARQL",
      aliases: ["rq"],
      case_insensitive: true,
      keywords: {
        keyword:
          "select construct describe ask where from named prefix base optional filter " +
          "union minus graph service bind values distinct reduced order by asc desc group " +
          "having limit offset as not exists in insert delete data load clear drop create " +
          "with using default all silent a",
        built_in:
          "str lang langmatches datatype bound iri uri bnode rand abs ceil floor round concat " +
          "strlen ucase lcase encode_for_uri contains strstarts strends strbefore strafter year " +
          "month day hours minutes seconds timezone tz now uuid struuid md5 sha1 sha256 sha384 " +
          "sha512 coalesce if strlang strdt sameterm isiri isuri isblank isliteral isnumeric " +
          "regex substr replace count sum min max avg sample group_concat",
        literal: "true false",
      },
      contains: [
        m.comment,
        m.iri,
        ...m.strings,
        m.languageTag,
        { className: "variable", begin: /[?$][\w]+/ },
        m.blankNode,
        m.prefixedName,
        m.number,
      ],
    };
  };
})();
