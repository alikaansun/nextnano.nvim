" Driven by tools/test_syntax.sh -- see there for how it is run.
syntax enable
filetype plugin on
set filetype=nextnano

let s:failed = 0

" Syntax group covering the first match of a:pat. The raw group is asserted
" rather than the resolved highlight: default links collapse Number, Float and
" Boolean onto Constant, which would make those checks vacuous.
function! s:Hi(pat) abort
  call cursor(1, 1)
  let l:lnum = search(a:pat, 'W')
  if l:lnum == 0
    return '<pattern not found>'
  endif
  let l:name = synIDattr(synID(l:lnum, col('.'), 1), 'name')
  return l:name ==# '' ? 'nextnanoNone' : l:name
endfunction

function! s:Expect(what, pat, want) abort
  let l:got = s:Hi(a:pat)
  if l:got !=# a:want
    echo printf('FAIL %-28s expected %s, got %s', a:what, a:want, l:got)
    let s:failed += 1
  else
    echo printf('ok   %-28s %s', a:what, l:got)
  endif
endfunction

call s:Expect('top-level group',      '\<global\>\ze{',                 'nextnanoGroupName')
call s:Expect('nested group',         '\<substrate\>\ze{',              'nextnanoGroupName')
call s:Expect('childless group',      '\<simulate3D\>',                  'nextnanoGroupName')
call s:Expect('attribute',            '\<temperature\>\ze = 300\.0',    'nnG_global_attr')
call s:Expect('deep attribute',       '\<max_num\>',                     'nnG_quantum_region_output_states_attr')
call s:Expect('integer',              '\<42\>',                          'nextnanoNumber')
call s:Expect('float',                '10\.5e-9',                        'nextnanoFloat')
call s:Expect('variable',             '\$WELL_WIDTH',                    'nextnanoVariable')
call s:Expect('builtin function',     '\<sqrt\>',                        'nextnanoFunction')
call s:Expect('unknown function',     '\<nosuchfunc\>',                  'nextnanoCall')
call s:Expect('boolean',              '\<yes\>',                         'nextnanoBoolean')
call s:Expect('comment',              '# Kelvin',                        'nextnanoComment')
call s:Expect('multi-line comment',   'Prose here',                      'nextnanoComment')
call s:Expect('string',               '"GaAs"',                          'nextnanoString')
call s:Expect('unquoted string value', '\<GaAs\>\s*#',                   'nextnanoNone')
call s:Expect('preprocessor',         '!IF',                             'nextnanoPreProc')
call s:Expect('xml tag',              '<sample\/>',                      'nextnanoTag')
call s:Expect('unknown keyword',      '\<regionn\>',                     'nextnanoUnknown')
call s:Expect('keyword in wrong group', '\<temperature\>\ze = 300\s',   'nextnanoUnknown')
" A group name is also accepted in attribute position ("SRH{ }" / "SRH = yes"),
" and an unknown group swallows its braces so the typo does not cascade.
call s:Expect('group used as attribute', '\<SRH\>',                       'nnG_currents_recombination_model_gattr')
call s:Expect('body of unknown group',  '\<contact\>\ze{',                'nextnanoGroupName')

" Completion is scoped to the group the cursor sits in.
call cursor(1, 1)
call search('\<quantum_spectra\>', 'W')
let s:items = map(luaeval("require('nextnano.complete').omnifunc(0, '')"), 'v:val.word')
for [s:word, s:want] in [['photogeneration', 1], ['temperature', 0], ['light_propagation', 1]]
  let s:got = index(s:items, s:word) >= 0
  if s:got != s:want
    echo printf('FAIL completion in optics{}     %s: expected %d, got %d', s:word, s:want, s:got)
    let s:failed += 1
  else
    echo printf('ok   completion in optics{}     %s', s:word)
  endif
endfor

if s:failed > 0
  echo printf('%d check(s) failed', s:failed)
  cquit!
endif
echo 'all checks passed'
quitall!
