(comment) @comment @spell
(string) @string
(variable) @variable
(number) @number
(boolean) @boolean
(directive) @keyword.directive
(operator) @operator
(assign) @operator
[(open) (close)] @punctuation.bracket
(punctuation) @punctuation.delimiter

; Same roles as syntax/nextnano.vim: a word before "{" names a group, a word
; before "=" an attribute, a word before "(" a function call.
(source (identifier) @keyword . (open))
(source (identifier) @property . (assign))
(source
  (identifier) @function.call
  .
  (punctuation) @_paren
  (#eq? @_paren "("))
