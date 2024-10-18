#!/usr/bin/env python3
# coding=utf-8
import math
import PIL.Image
from PIL import ImageDraw
import numpy as np
import svgutils.transform as sg

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

WOOD_DEPTH = 3  # mm

OFFSET_BETWEEN_LINES = WOOD_DEPTH / 2    # mm
VERY_MIN_LINE_HEIGHT = 3    # mm
MIN_LINE_HEIGHT = 15    # mm
SPACE_HEIGHT = WOOD_DEPTH    # mm

FILE_NAME_STEM = 'baleine_test2'
SVG_FILE_IN_SVG = f'{FILE_NAME_STEM}.svg'
SVG_FILE_IN_PNG = f'{FILE_NAME_STEM}.png'
SVG_FILE_OUT_SVG = f'{FILE_NAME_STEM}_out.svg'
SVG_FILE_OUT_PNG = f'{FILE_NAME_STEM}_out.png'

input_svg = sg.fromfile(SVG_FILE_IN_SVG)

# we create a png temp file from the svg to rasterize the picture
svg_to_raster = svg2rlg(SVG_FILE_IN_SVG)
svg_to_raster.scale(1, 1)
image = renderPM.drawToPIL(svg_to_raster)
viewbox = list([float(i) for i in input_svg.root.attrib['viewBox'].split()])

data = np.asarray(image)
out_img = image.copy()
lines_to_draw = []

rows, cols, _ = data.shape

channel = data[:, :, 0]
im = PIL.Image.fromarray(channel)
image.save(SVG_FILE_IN_PNG)

x_scale = viewbox[2] / image.width
y_scale = viewbox[3] / image.height

OFFSET_BETWEEN_LINES = round(OFFSET_BETWEEN_LINES / x_scale)
VERY_MIN_LINE_HEIGHT = round(VERY_MIN_LINE_HEIGHT / y_scale)
MIN_LINE_HEIGHT = round(MIN_LINE_HEIGHT / y_scale)
SPACE_HEIGHT = round(SPACE_HEIGHT / y_scale)

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
        
        indexes = [x for x,v in list(enumerate(col)) if v != 255]
        start_row = np.min(indexes)
        end_row = start_row
        
        while end_row < image.height and col[end_row] != 255:
            end_row += 1
            
        # we go back one row
        end_row -= 1
        
        # we got an area to fill
        col_finished = False
        while not col_finished:           
            full_height = end_row - start_row
                   
            if cols_drawn % 2 == 0:
                # even line
                # we begin with a space
                # and we draw a line with a max length of fh
                # or the remaining height
                # and we redo until the end
                
                current_y = start_row
                finished = False
                while not finished:
                    if current_y + SPACE_HEIGHT < end_row:
                        current_y += SPACE_HEIGHT
                        lh = min(MIN_LINE_HEIGHT, end_row - current_y)
                        end_y = current_y + lh
                    
                        lines_to_draw.append((col_index, current_y, col_index, end_y))
                    
                        current_y = end_y
                    
                        if end_y == end_row:
                            finished = True
                    else:
                        finished = True
                    
            else:
                # we do the same beginning by the end
                current_y = end_row
                finished = False
                while not finished:
                    if current_y - SPACE_HEIGHT > start_row:
                        current_y -= SPACE_HEIGHT
                        lh = min(MIN_LINE_HEIGHT, current_y - start_row)
                        end_y = current_y - lh
                    
                        lines_to_draw.append((col_index, current_y, col_index, end_y))
                    
                        current_y = end_y
                    
                        if end_y == start_row:
                            finished = True
                    else:
                        finished = True
                
            start_row = end_row + 1
            # looking for next shape
            while start_row < image.height and col[start_row] == 255:
                start_row += 1
            
            if start_row >= image.height:
                col_finished = True
            
            # looking for the end row
            end_row = start_row
            while end_row < image.height and col[end_row] != 255:
                end_row += 1
                
            # we go back one row
            end_row -= 1
            
        cols_drawn += 1
    col_index += OFFSET_BETWEEN_LINES

draw = ImageDraw.Draw(out_img) 

print(f'x scale = {x_scale}, y scale = {y_scale}')
for (x1, y1, x2, y2) in lines_to_draw:
    
    draw.line((x1, y1, x2, y2), fill=(255, 0, 0, 255))
    input_svg.append(sg.LineElement([(x1 * x_scale, y1 * y_scale), (x2 * x_scale, y2 * y_scale)], color="blue"))
    
input_svg.save(SVG_FILE_OUT_SVG)

out_img.save(SVG_FILE_OUT_PNG)
out_img.show()
