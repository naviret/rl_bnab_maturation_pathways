import pymol 
from pymol import cmd 

def get_colors():
    """ 
    Colors for RFdiffusion
    """
    cmd.set_color("good_gray",       [220,220,220]) #dcdcdc
    cmd.set_color("good_teal",      [ 0.310, 0.725, 0.686 ]) #4FB9AF
    cmd.set_color("good_navaho",     [255,224,172]) #FFE0AC
    cmd.set_color("good_melon",      [255,198,178]) #FFC6B2
    cmd.set_color("good_pink",       [255,172,183]) #FFACB7
    cmd.set_color("good_purple",     [213,154,181]) #D59AB5
    cmd.set_color("good_lightblue",  [149,150,198]) #9596C6
    cmd.set_color("good_blue",       [102,134,197]) #6686C5
    cmd.set_color("good_darkblue",   [75,95,170]) #4B5FAA


def get_lighting():
    """ 
    Lighting for RFdiffusion
    Credit: Sam Pellock
    """
    cmd.do('set specular, 0')
    cmd.do('set ray_shadow, off')
    cmd.do('set valence, off')
    cmd.do('set antialias, 2')
    cmd.do('set ray_trace_mode, 1')
    cmd.do('set ray_trace_disco_factor, 1')
    cmd.do('set ray_trace_gain, 0.1')
    cmd.do('set power, 0.2')
    cmd.do('set ambient, 0.4')
    cmd.do('set ray_trace_color, gray30')

cmd.extend('get_colors',get_colors)
cmd.extend('get_lighting', get_lighting)

