from pymol import cmd 

# Find bonds between heavy chain and antigen && light chain and antigen
H_I = cmd.find_pairs("heavy_paratopeAtoms", "heavy_epitopeAtoms", cutoff=4.5, mode=0)
L_I = cmd.find_pairs("light_paratopeAtoms", "light_epitopeAtoms", cutoff=4.5, mode=0)
print("number of heavy interactions:", len(H_I))
print("number of light interactions:", len(L_I))