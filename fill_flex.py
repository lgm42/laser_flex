#!/usr/bin/env python3
# coding=utf-8
import math
import PIL.Image
from PIL import ImageDraw
import numpy as np
import svgutils.transform as sg

OFFSET_BETWEEN_LINES = 5
VERY_MIN_LINE_HEIGHT = 3
MIN_LINE_HEIGHT = 20
SPACE_HEIGHT = 10

FILE_NAME_STEM = 'baleine_test'
SVG_FILE_IN_SVG = f'{FILE_NAME_STEM}.svg'
SVG_FILE_IN_PNG = f'{FILE_NAME_STEM}.png'
SVG_FILE_OUT_SVG = f'{FILE_NAME_STEM}_out.svg'
SVG_FILE_OUT_PNG = f'{FILE_NAME_STEM}_out.png'

input_svg = sg.fromfile(SVG_FILE_IN_SVG)

image = PIL.Image.open(SVG_FILE_IN_PNG)
data = np.asarray(image)
out_img = image.copy()
lines_to_draw = []
print(data.shape) # (height, width, channels)

rows, cols, _ = data.shape

channel = data[:, :, 0]
im = PIL.Image.fromarray(channel)
im.save("forme_test.jpg")

# looking for the index of the cols
cols_to_manage = list([x[0] for x in enumerate(channel.T) if any([(y != 255) for y in x[1]])])
start_col = np.min(cols_to_manage)
end_col = np.max(cols_to_manage)

cols_drawn = 0
col_index = start_col + OFFSET_BETWEEN_LINES
# iterate from the left looking for the first column with pixels
while col_index < end_col:
    col = channel[:, col_index]
    if any(item in col for item in col if item != 255):
        print(f'{col_index}')
        # looking for the first row and the last
        #getting data with values
        indexes = [x for x,v in list(enumerate(col)) if v != 255]
        start_row = np.min(indexes)
        end_row = np.max(indexes)
        print(f'col {col_index}: start row {start_row}, end row {end_row}')
        
        full_height = end_row - start_row
        current_y = start_row
        
        if cols_drawn % 2 == 0:
            # even line, we begin with a line and finish with a line inserting as many spaces and lines as needed
            # LSLS....L
            # with 58 pixels height and a min line height of 20 px
            # we have 2 lines of 24 pixels sperated by a space of 10 px
            # there it is at least 2 lines and there lines -1 spaces
            # n must be an integer
            # full_height = n * lines + (n - 1) * spaces
            # fh = n * l + n * s - s
            # fh + s = n (l + s)
            # n = (fh + s) / (l + s)
            # we take entire div round to the lower and determine l
            # l + s = (fh + s) / n
            # l = (fh + s) / n - s
            
            # check if it too small
            if SPACE_HEIGHT + 2 * MIN_LINE_HEIGHT > full_height:
                # two cases no space to put a small line each side, we do nothing
                # or we compute the size of the lines
                if SPACE_HEIGHT + 2 * VERY_MIN_LINE_HEIGHT > full_height:
                    # we do nothing
                    n = 0
                else:
                    n = 2
                    l = np.floor((full_height - SPACE_HEIGHT) / 2)
            else:       
                n = (full_height + SPACE_HEIGHT) / (MIN_LINE_HEIGHT + SPACE_HEIGHT)
                n = math.floor(n)
                l = (full_height + SPACE_HEIGHT) / n - SPACE_HEIGHT
        else:
            # odd line, the same but we begin with a space and we have space - 1 lines
            # fh = n * l + n * s + s
            # fh - s = n (l + s)
            # n = (fh - s) / (l + s)
            # we take entire div round to the lower and determine l
            # l + s = (fh - s) / n
            # l = (fh - s) / n - s
            # check if it too small
            if SPACE_HEIGHT * 2 + MIN_LINE_HEIGHT > full_height:
                # two cases no space to put a small line and two spaces, we do nothing
                # or we compute the size of the line
                if SPACE_HEIGHT * 2 + VERY_MIN_LINE_HEIGHT > full_height:
                    # we do nothing
                    n = 0
                else:
                    n = 1
                    l = full_height - SPACE_HEIGHT * 2
                    current_y += SPACE_HEIGHT
            else:  
                n = (full_height - SPACE_HEIGHT) / (MIN_LINE_HEIGHT + SPACE_HEIGHT)
                n = math.floor(n)
                l = (full_height - SPACE_HEIGHT) / n - SPACE_HEIGHT
                # we offset the first line by a space
                current_y += SPACE_HEIGHT
        for i in range(n):
            lines_to_draw.append((col_index, current_y, col_index, current_y + l))
            current_y = current_y + l + SPACE_HEIGHT
        cols_drawn += 1
    col_index += OFFSET_BETWEEN_LINES

draw = ImageDraw.Draw(out_img) 
for (x1, y1, x2, y2) in lines_to_draw:
    draw.line((x1, y1, x2, y2), fill=(255, 0, 0, 255))

out_img.save(SVG_FILE_OUT_PNG)
out_img.show()
# layout = ColumnLayout(5)

# svg = fromfile("forme_test.svg")
# layout.add_figure(svg)

# layout.save("out.svg")