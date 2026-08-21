if exists("b:current_syntax")
  finish
endif

syn case match

" Values and trivia. These are shared by every group, and by the file scope, via
" the @nextnanoCommon cluster the generated group regions pull in.
syn match  nextnanoComment "#.*$" contains=@Spell
syn region nextnanoComment start="^\s*!TEXT\>" end="^\s*!ENDTEXT\>" keepend contains=@Spell

syn region nextnanoString start=+"+ skip=+\\.+ end=+"+ contains=nextnanoEscape
syn match  nextnanoEscape "\\." contained

syn match  nextnanoVariable "\$\w\+"
syn keyword nextnanoBoolean yes no

" Floats last: "10" matches the integer rule at the same position inside
" "10.5e-9", and of two items starting together the later definition wins.
syn match  nextnanoNumber "\<\d\+\>"                         display
syn match  nextnanoFloat  "\<\d\+\.\d*\%([eE][-+]\=\d\+\)\=" display
syn match  nextnanoFloat  "\<\d\+[eE][-+]\=\d\+\>"           display

syn match  nextnanoPreProc "^\s*!\%(IF\|ELIF\|ELSE\|ENDIF\|WHEN\|VARS\|TABLE\|DATA\)\>"
syn match  nextnanoOperator "[-+*/%^~]\|[<>!=]=\|[<>]\|&&\|||"
" Root-level XML tags; the parser ignores them. After the operators on purpose,
" so "<id/>" wins over the comparison operators it contains.
syn match  nextnanoTag "<\/\=\w\+\/\=>"

" A word before "(" is a function call, and only the documented built-ins are
" valid. The keyword list is contained, so it colours the call only where the
" name is real; everything else stays flagged.
syn match nextnanoCall "\<\w\+\>\ze(" contains=nextnanoFunction
syn keyword nextnanoFunction contained
      \ sqrt cbrt exp log ln log2 log10 sin cos tan asin acos atan sinh cosh
      \ tanh asinh acosh atanh erf erfc gamma fdm3half fdmhalf fdzero fdphalf
      \ fdp3half abs floor ceil round sign heaviside ispositive isnegative
      \ iszero isnotpositive isnotnegative isnotzero string dim

syn cluster nextnanoCommon contains=nextnanoComment,nextnanoString,nextnanoVariable,
      \ nextnanoBoolean,nextnanoFloat,nextnanoNumber,nextnanoPreProc,nextnanoTag,
      \ nextnanoOperator,nextnanoCall

" Any word in group or attribute position that no keyword list claimed. Defined
" before the generated groups on purpose: Vim gives priority to the item defined
" last, so every real keyword region overrides this one. Only names directly
" before "{" or "=" are ever tested, so values on the right of "=" -- numbers,
" $variables, yes/no, quoted and unquoted strings -- are never flagged.
syn match nextnanoUnknown "\<\w\+\>\ze\_s*[{=]"

" An unrecognised group still has to swallow its braces, or its closing "}"
" would end the enclosing group and flag everything after it. Its body is left
" alone: with no valid parent there is nothing to check the contents against.
syn region nextnanoUnknownGroup matchgroup=nextnanoUnknown start="\<\w\+\>\_s*{"
      \ matchgroup=nextnanoDelim end="}"
      \ contains=@nextnanoCommon,nextnanoAnyGroup
syn region nextnanoAnyGroup matchgroup=nextnanoGroupName start="\<\w\+\>\_s*{"
      \ matchgroup=nextnanoDelim end="}" contained
      \ contains=@nextnanoCommon,nextnanoAnyGroup

runtime! syntax/nextnano_keywords.vim

syn sync minlines=50

hi def link nextnanoComment      Comment
hi def link nextnanoString       String
hi def link nextnanoEscape       SpecialChar
hi def link nextnanoVariable     Identifier
hi def link nextnanoNumber       Number
hi def link nextnanoFloat        Constant
hi def link nextnanoBoolean      Boolean
hi def link nextnanoPreProc      PreProc
hi def link nextnanoTag          Special
hi def link nextnanoOperator     Operator
hi def link nextnanoFunction     Function
hi def link nextnanoGroupName    Statement
hi def link nextnanoAttribute    Keyword
hi def link nextnanoDelim        Delimiter

" Unrecognised keywords are an error by default. Set this to 0 if the
" documentation the keyword lists were generated from is behind your nextnano
" version, or you use keywords it no longer documents.
if get(g:, "nextnano_highlight_unknown", 1)
  hi def link nextnanoUnknown Error
  hi def link nextnanoCall    Error
else
  hi def link nextnanoUnknown NONE
  hi def link nextnanoCall    NONE
endif

let b:current_syntax = "nextnano"
