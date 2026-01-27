// Prettier plugin to strip trailing non-breaking spaces from markdown files
const markdown = require('prettier/parser-markdown');

module.exports = {
  parsers: {
    markdown: {
      ...markdown.parsers.markdown,
      parse(text, parsers, options) {
        // Remove trailing non-breaking spaces (U+00A0) and other Unicode whitespace at end of lines
        // This handles both lines that end with non-breaking spaces and lines that are entirely non-breaking spaces
        let cleaned = text
          // Remove trailing Unicode whitespace (non-breaking spaces, etc.) at end of lines
          .replace(/[\u00A0\u2000-\u200B\u202F\u205F\u3000]+$/gm, '')
          // Also remove lines that are entirely Unicode whitespace (non-breaking spaces)
          .replace(/^[\u00A0\u2000-\u200B\u202F\u205F\u3000]+\n/gm, '\n');

        // Convert leading non-breaking spaces to regular spaces
        // This fixes formatting issues where NBSP at the start of lines prevents proper paragraph/list formatting
        cleaned = cleaned.replace(/^([\u00A0\u2000-\u200B\u202F\u205F\u3000]+)/gm, (match) => ' '.repeat(match.length));

        // Convert non-breaking spaces before markdown list markers to regular spaces
        // This fixes formatting issues where NBSP prevents proper list item recognition
        cleaned = cleaned.replace(/([\s]*)[\u00A0\u2000-\u200B\u202F\u205F\u3000]+([-*+]\s)/gm, '$1$2');

        // Use the original markdown parser
        return markdown.parsers.markdown.parse(cleaned, parsers, options);
      },
    },
  },
  printers: markdown.printers,
  languages: markdown.languages,
};
