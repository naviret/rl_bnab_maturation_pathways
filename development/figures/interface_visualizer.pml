run rfdiffusion_pymol_sets.py 
get_lighting
get_colors


select heavy, /6mtt//H 
select light, /6mtt//L 
select antigen, /6mtt//P
select antibody, heavy|light


color good_gray, antibody
color good_lightblue, heavy
color good_blue, antigen


select paratopeAtoms, antibody within 4.5 of antigen 
select epitopeAtoms, antigen within 4.5 of antibody
select heavy_paratopeAtoms, heavy within 4.5 of antigen 
select heavy_epitopeAtoms, antigen within 4.5 of heavy
select light_paratopeAtoms, light within 4.5 of antigen 
select light_epitopeAtoms, antigen within 4.5 of light


select paratopeRes, byres paratopeAtoms
select epitopeRes, byres epitopeAtoms
select heavy_paratopeRes, byres heavy_paratopeAtoms
select heavy_epitopeRes, byres heavy_epitopeAtoms
select light_paratopeRes, byres light_paratopeAtoms
select light_epitopeRes, byres light_epitopeAtoms


distance interactions, paratopeAtoms, epitopeAtoms, 4.5, 0
distance heavy_interactions, heavy_paratopeAtoms, heavy_epitopeAtoms, 4.5, 0
distance light_interactions, light_paratopeAtoms, light_epitopeAtoms, 4.5, 0


color red, interactions
hide labels, interactions
hide labels, heavy_interactions
hide labels, light_interactions

hide heavy_interactions
hide light_interactions


show sticks, paratopeRes
show sticks, epitopeRes


set cartoon_side_chain_helper, on


set sphere_quality, 2
set sphere_scale, 0.3
show spheres, paratopeAtoms
show spheres, epitopeAtoms


color good_teal, paratopeAtoms
color good_darkblue, epitopeAtoms


set dash_transparency, 0.75


set ray_trace_mode, 1


run bond_counter.py