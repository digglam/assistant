'''

An experimental image cropping program for cleaning up scanned images.

@author: Agusti Pellicer (Aalto University)

'''


from wand.image import Image
from wand.display import display
import wand
import numpy
import itertools


import glob
import os

#FILE_NAME = "2013-09-24T16:07:36.239799-t.png"
#FILE_NAME = "test-t.png"
#FILE_NAME = "2013-09-24T16:11:56.134432.png"
#FILE_NAME = "2013-10-08T10:56:16.120243-t.png"
#FILE_NAME = "2013-10-08T14:06:46.305716-t.png"
#im = Image(filename=FILE_NAME)

'''
Basis of the algorithm:

- Take the middle of the image, check std deviation
- Take the upper half and the lower half
- Compare them if they are vastly different we could see where is the picture and try to delimite the region

'''
def crop_image(image):
    lines = [0] * 3
    #Init first lines to test
    lines[0] = image.height/2

    lines[1] = lines[0]/2

    lines[2] = lines[0] + lines[1]


    stick_lines = [0] * 3
    count_lines = 0


    difference_to_middle_top = []
    difference_to_middle_bottom = []

    difference_to_middle_top.append(0)
    difference_to_middle_bottom.append(image.height)
    while count_lines < 100:
        #Color for the different lines
        color1 = []
        color2 = []
        color3 = []

        for col in image[lines[0]]:
            color1.append(col.red_int8)

        for col in image[lines[1]]:
            color2.append(col.red_int8)

        for col in image[lines[2]]:
            color3.append(col.red_int8)


        maxstd = []
        first_std = numpy.std(color1)
        maxstd.append(first_std)
        second_std = numpy.std(color2)
        maxstd.append(second_std)
        third_std = numpy.std(color3)
        maxstd.append(third_std)

        print "Middle line: %d Top line: %d Bottom line: %d" % (lines[0], lines[1], lines[2])
        print "Middle: %d Top: %d Bottom: %d" % (first_std, second_std, third_std)

        '''
        Now we have to choose what to do:
        If no lines let's search more?
        If there's one line in the picture, that's the new middle line
        If there are two lines in the picture, the one that is not on the picture should move closer and viceversa
        If there are the three lines we should move the two more apart from the first one

        '''
        count = 0
        if first_std > 15:
            count = count + 1
        if second_std > 15:
            count = count + 1
        if third_std > 15:
            count = count + 1

        print "Lines in %d" % count
        if count == 1:
            if maxstd.index(max(maxstd)) == 0:
                stick_lines[0] = 1
                difference_to_middle_top.append(lines[1])
                difference_to_middle_bottom.append(lines[2])
                lines[1] = lines[1] + lines[1]/8
                lines[2] = lines[2] - lines[2]/8
                
            elif stick_lines[0] == 0:
                lines[0] = lines[maxstd.index(max(maxstd))]
                lines[1] = lines[0]/2
                lines[2] = lines[0] + lines[1]
        if count == 2:
            #We don't change the middle one
            lines[0] = lines[0]
            if second_std > 15:
                #Move it half up
                if lines[1] - lines[1]/4 < 0:
                    lines[1] = 0
                else:
                    lines[1] = lines[1] - lines[1]/4
            else:
                difference_to_middle_top.append(lines[1])
                lines[1] = lines[1] + lines[1]/4
            if third_std > 15:
                #Move it half down
                if lines[2] + lines[2]/4 > image.height -1:
                    lines[2] = image.height - 1
                else:
                    lines[2] = lines[2] + lines[2]/4
            else:
                difference_to_middle_bottom.append(lines[2])
                lines[2] = lines[2] - lines[2]/4
        if count == 3:
            lines[0] = lines[0]
            if lines[1] - lines[1]/4 < 0:
                lines[1] = 0
            else:
                lines[1] = lines[1] - lines[1]/4
            if lines[2] + lines[2]/4 > image.height -1:
                lines[2] = image.height - 1
            else:
                lines[2] = lines[2] + lines[2]/4

        print "Middle line: %d Top line: %d Bottom line: %d" % (lines[0], lines[1], lines[2])

        #See how many 1s we have
        #count_lines = stick_lines.count(1)
        print "Stick lines count: %d" % count_lines
        count_lines = count_lines + 1

    lines[1] = max(difference_to_middle_top)
    lines[2] = min(difference_to_middle_bottom)

    return lines


#For all the png in the folder
for filename in glob.glob("*-t.png"):
    im = Image(filename=filename)
    #Save the widht and height of the thumbnail
    th = im.height
    tw = im.width
    #Crop the image
    l = crop_image(im)
    top = l[1]
    bottom = l[2]
    im.crop(0,l[1],im.width,l[2])
    #We rotate so we can use the same code!
    im.rotate(90)
    print im.height, im.width
    l = crop_image(im)
    im.crop(0,l[1],im.width,l[2])
    left = l[1]
    right = l[2]
    im.rotate(-90)
    #We open the original image so we can crop it too
    original = filename.replace('-t','')
    oim = Image(filename=original)
    ow = oim.width
    oh = oim.height
    oim.crop((left * ow) /tw,(top * oh) / th,(right * ow) / tw,(bottom * oh) / th)
    im.save(filename=filename+'crop.png')
    oim.save(filename=original+'crop.png')