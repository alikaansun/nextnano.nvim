{
  lib,
  vimUtils,
  tree-sitter,
}:

vimUtils.buildVimPlugin {
  pname = "nextnano.nvim";
  version = "0.2.0";
  src = lib.cleanSource ./.;

  # For embedded input (e.g. strings in Python); see tree-sitter/grammar.js.
  passthru.grammar = tree-sitter.buildGrammar {
    language = "nextnano_in";
    version = "0.1.0";
    src = lib.cleanSource ./tree-sitter;
    generate = true;
  };

  meta = {
    description = "Syntax highlighting for nextnano++ input files in Neovim";
    homepage = "https://github.com/alikaansun/nextnano.nvim";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ alikaansun ];
  };
}
