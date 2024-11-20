{ lib
, python3
, writeScriptBin
, nh
}:

let
  pname = "nay";
  version = "0.1.0";
  

  script = writeScriptBin pname ''
    #!${python3}/bin/python3
    import os
    # Ensure nh is in PATH
    os.environ["PATH"] = "${nh}/bin:" + os.environ["PATH"]
    ${builtins.readFile ./nay.py}
  '';

in
script // {
  meta = with lib; {
    description = "Interactive NixOS package installer (like yay for NixOS)";
    longDescription = ''
      A tool that searches for NixOS packages using nh search, allows interactive
      selection, and automatically adds them to configuration.nix with system rebuild.
    '';
    homepage = "https://github.com/christhepanda28/nay";
    platforms = platforms.linux;
    maintainers = with maintainers; [ christhepanda28];
    mainProgram = pname;
  };
}
