// A flat token stream, not a parse of the nesting. It exists to highlight
// nextnano++ input embedded in other files, e.g. Python f-strings, where
// braces come doubled ("{{") and interpolations leave holes mid-group, so a
// structural grammar would drown in errors. Whole .in files keep
// syntax/nextnano.vim; the language is named nextnano_in, not nextnano, so
// Neovim never starts it on that filetype.
module.exports = grammar({
  name: "nextnano_in",

  word: ($) => $.identifier,

  // \t and \n count as whitespace: in a host-language string they are escapes.
  extras: (_) => [/\s/, /\\[nt]/],

  rules: {
    source: ($) =>
      repeat(
        choice(
          $.comment,
          $.string,
          $.variable,
          $.number,
          $.boolean,
          $.directive,
          $.identifier,
          $.open,
          $.close,
          $.assign,
          $.operator,
          $.punctuation,
        ),
      ),

    comment: (_) => token(seq("#", /.*/)),
    string: (_) => token(choice(/"([^"\\\n]|\\.)*"/, /'([^'\\\n]|\\.)*'/)),
    variable: (_) => /\$\w+/,
    number: (_) => /\d+(\.\d*)?([eE][-+]?\d+)?/,
    boolean: (_) => choice("yes", "no"),
    directive: (_) => /![A-Z]+/,
    identifier: (_) => /[A-Za-z_]\w*/,

    // Group braces are named nodes so highlights.scm can anchor on them.
    open: (_) => choice("{", "{{"),
    close: (_) => choice("}", "}}"),
    assign: (_) => "=",

    operator: (_) =>
      choice("+", "-", "*", "/", "%", "^", "~", "<", ">", "<=", ">=", "==", "!=", "&&", "||"),
    punctuation: (_) => choice("[", "]", "(", ")", ",", ";", ":", "."),
  },
});
