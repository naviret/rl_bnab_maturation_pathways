select antibody, /2fx7//H+L 
select antigen, /2fx7//P


color good_gray, antibody
color good_lightblue, /2fx7//H
color good_blue, antigen

select paratopeAtoms, antibody within 4.5 of antigen 
select epitopeAtoms, antigen within 4.5 of antibody

select paratopeRes, byres paratopeAtoms
select epitopeRes, byres epitopeAtoms

distance interactions, paratopeAtoms, epitopeAtoms, 4.5, 0

color red, interactions
hide labels, interactions

show sticks, paratopeRes
show sticks, epitopeRes

set cartoon_side_chain_helper, on

set sphere_quality, 2
set sphere_scale, 0.3
show spheres, paratopeAtoms
show spheres, epitopeAtoms

color good_teal, paratopeAtoms
color good_darkblue, epitopeAtoms

set dash_transparency, 0.5

set ray_trace_mode, 1
