{
  lib,
  vimUtils,
}:

vimUtils.buildVimPlugin {
  pname = "nextnano.nvim";
  version = "0.2.0";
  src = lib.cleanSource ./.;

  meta = {
    description = "Syntax highlighting for nextnano++ input files in Neovim";
    homepage = "https://github.com/alikaansun/nextnano.nvim";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ alikaansun ];
  };
}
