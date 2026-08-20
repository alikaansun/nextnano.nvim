if exists("b:current_syntax")
  finish
endif

syn keyword nextnanoConditional if while for return
syn keyword nextnanoBoolean     yes no
syn keyword nextnanoSection     global structure grid import impurities classical
syn keyword nextnanoSection     strain poisson quantum contacts currents cbr
syn keyword nextnanoSection     optics database output run remove

syn match nextnanoNumber   "\<\d\+\>"
syn match nextnanoFloat    "\<\d\+e[-+]\=\d\+\>"           display
syn match nextnanoFloat    "\<\d\+\.\d*\(e[-+]\=\d\+\)\="  display
syn match nextnanoVariable "\$\w\+"

syn region nextnanoString start=+"+ skip=+\\.+ end=+"+ contains=nextnanoEscape
syn match  nextnanoEscape "\\." contained

syn match nextnanoComment "#.*$" contains=@Spell

hi def link nextnanoComment     Comment
hi def link nextnanoString      String
hi def link nextnanoEscape      SpecialChar
hi def link nextnanoVariable    Identifier
hi def link nextnanoNumber      Number
hi def link nextnanoFloat       Float
hi def link nextnanoBoolean     Boolean
hi def link nextnanoConditional Conditional
hi def link nextnanoSection     Function

let b:current_syntax = "nextnano"
