#!/bin/csh

#mkdir pdb_babel
foreach lig (`ls -d LIG*`)
    cd "$lig"
    set a = `ls *pdb`
    set name = `basename $a .pdbqt`
    babel -ipdb "$a" -omol2 ../mol2/"$name".mol2 -f 1 -l 1 -h -p 7
    cd ..
end

