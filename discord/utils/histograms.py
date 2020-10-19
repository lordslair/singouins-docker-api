# -*- coding: utf8 -*-
# Forked and modified from nk412/quickhist

import sys

from numpy import array,histogram,percentile
from math  import floor

# Constants
CHARS  = {'full_top':'┃', 'half_top':'╻', 'fill':'┃'}
width  = 50
height = 10

# Example
# input_list = ['1','1','2','2','2','2','2','5']

def draw(input_list):

    answer = '```'+"\n"

    # Convert input to floats
    try:
        input_list = array(input_list, float)
    except:
        raise SystemError("Failed to convert input to float")

    # Calculate shape
    shape = ( min(input_list), max(input_list) )

    hist_list,bin_edges = histogram(input_list,bins=width)
    max_count = max(hist_list)

    normed_hist_list = [ float(x)*height/max_count for x in hist_list ]

    # TODO make the offset configurable
    y_offset = '       '
    y_label  = ' prop. '

    answer += "\n"
    # Build plot from top level
    for depth in range(height-1,-1,-1):

        # Draw Y axis
        if depth == height/2:
            answer += y_label + '│'
        else:
            answer += y_offset + '│'

        # Draw bars
        for item in normed_hist_list:
            floored_item = floor(item)
            if floored_item >= depth:
                if floored_item == depth and item % 1 < 0.75 and item%1 >0.25:
                    answer += CHARS['half_top']
                elif floored_item == depth and item % 1 > 0.75 :
                    answer += CHARS['full_top']
                elif floored_item > depth:
                    answer += CHARS['fill']
                else:
                    answer += ' '
                continue
            else:
                answer += ' '
        answer += "\n"

    # Draw X axis
    answer += y_offset + '└'+ "─"*(width+2) + "\n"
    answer += y_offset + str(shape[0]) + ' '*(width-3) + str(shape[1]) + "\n"

    # Calculate stats on data
    answer += f'count      : {len(input_list)}\n'
    for perc in [25,50,75]:
        answer += "{}th perc. : {}\n".format(perc, percentile(input_list,perc))

    answer += '```'

    return answer
