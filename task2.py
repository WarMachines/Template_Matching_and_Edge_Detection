"""
Character Detection
(Due date: March 8th, 11: 59 P.M.)

The goal of this task is to experiment with template matching techniques. Specifically, the task is to find ALL of
the coordinates where a specific character appears using template matching.

There are 3 sub tasks:
1. Detect character 'a'.
2. Detect character 'b'.
3. Detect character 'c'.

You need to customize your own templates. The templates containing character 'a', 'b' and 'c' should be named as
'a.jpg', 'b.jpg', 'c.jpg' and stored in './data/' folder.

Please complete all the functions that are labelled with '# TODO'. Whem implementing the functions,
comment the lines 'raise NotImplementedError' instead of deleting them. The functions defined in utils.py
and the functions you implement in task1.py are of great help.

Hints: You might want to try using the edge detectors to detect edges in both the image and the template image,
and perform template matching using the outputs of edge detectors. Edges preserve shapes and sizes of characters,
which are important for template matching. Edges also eliminate the influence of colors and noises.

Do NOT modify the code provided.
Do NOT use any API provided by opencv (cv2) and numpy (np) in your code.
Do NOT import any library (function, module, etc.).
"""


import argparse
import json
import os

import utils
from task1 import *   # you could modify this line


def parse_args():
    parser = argparse.ArgumentParser(description="cse 473/573 project 1.")
    parser.add_argument(
        "--img_path", type=str, default="./data/src.jpg",
        help="path to the image used for character detection (do not change this arg)")
    parser.add_argument(
        "--template_path", type=str, default="./data/a.jpg",
        choices=["./data/a.jpg", "./data/b.jpg", "./data/c.jpg"],
        help="path to the template image")
    parser.add_argument(
        "--result_saving_directory", dest="rs_directory", type=str, default="./results/",
        help="directory to which results are saved (do not change this arg)")
    args = parser.parse_args()
    return args


def detect_characters(img, template, threshold):
    
    tem_height = len(template)
    tem_width = len(template[0])
    
    result_normalised = []
    for i in range(0,len(img)-tem_height+1):
        row = []
        for j in range(0,len(img[0])-tem_width+1):
            sum_of_product_image_template = 0
            sum_of_square_image = 0
            sum_of_square_template = 0
            for xindex in range(0,tem_height):
                for yindex in range(0,tem_width):
                    sum_of_product_image_template += int(img[i+xindex][j+yindex])*int(template[xindex][yindex])
                    sum_of_square_image += int(img[i+xindex][j+yindex])*int(img[i+xindex][j+yindex])
                    sum_of_square_template += int(template[xindex][yindex])*int(template[xindex][yindex])
            
            
            denominator  = np.sqrt( sum_of_square_image*sum_of_square_template)
            normalize_value = sum_of_product_image_template/denominator
            row.append(normalize_value)
        result_normalised.append(row)
    

    coordinates = []
    for i in range(0,len(result_normalised)):
        for j in range(0,len(result_normalised[0])):
            if result_normalised[i][j] > threshold:
                coordinates.append([i,j]) 

    coordinates = sorted(coordinates, key=lambda x: x[0])
    coordinates = filter_coordinates(coordinates, tem_height, tem_width)
    coordinates = sorted(coordinates, key=lambda x: x[1])
    return filter_coordinates(coordinates, tem_height, tem_width)

def detect(img,template):
    """Detect a given character, i.e., the character in the template image.

    Args:
        img: nested list (int), image that contains character to be detected.
        template: nested list (int), template image.

    Returns:
        coordinates: list (tuple), a list whose elements are coordinates where the character appears.
            format of the tuple: (x (int), y (int)), x and y are integers.
            x: row that the character appears (starts from 0).
            y: column that the character appears (starts from 0).
    """
    # TODO: implement this function.
    #raise NotImplementedError
    args = parse_args()
    name = os.path.splitext(os.path.split(args.template_path)[1])[0]
    data = define_parameters()
    coordinates = detect_characters(img,template,data[name]["zero"])
    if name == 'b':
        coordinates+= detect_characters(img, reduce_template_by_one_level(template),data[name]["one"])
        coordinates+= detect_characters(img, reduce_template_by_half_level(template),data[name]["half"])

    return coordinates


def reduce_template_by_one_level(template):
    subsample = []
    for i in range(0,int(len(template)/2)):
        row = []
        for j in range(0,int(len(template[0])/2)):
            value = (int(template[(i*2)][(j*2)]) + int(template[(i*2)][(j*2)+1]) + int(template[(i*2)+1][(j*2)]) + int(template[(i*2)+1][(j*2)+1]))/4
            row.append(value)
        subsample.append(row)
    
    return subsample

def reduce_template_by_half_level(template):
    subsample = []
    i = 0
    flag = True
    while i + 2 < len(template):
        row = []
        j = 0
        while j + 2 < len(template[0]):
            if j + 3 <= len(template[0]):
                value = int(template[i][j]) + int(template[i + 1][j]) + int(template[i][j + 1]) + int(template[i + 1][j + 1])
                row.append(value / 4)

                value = int(template[i][j + 1]) + int(template[i + 1][j + 1]) + int(template[i][j + 1 + 1]) + int(template[i + 1][j + 1 + 1])
                row.append(value / 4)

            elif j + 2 <= len(template[0]):
                value = int(template[i][j]) + int(template[i + 1][j]) + int(template[i][j + 1]) + int(template[i + 1][j + 1])
                row.append(value / 4)
            j += 3
        
        if flag:
            i += 1
            flag = False
        else:
            i += 2
            flag = True

        subsample.append(row)

    return subsample

def define_parameters():
    a = { "zero": 0.956}
    b = {"zero" : 0.970, "half" : 0.970, "one" : 0.9697}
    c = {"zero" : 0.978}

    data = {"a" : a, "b" : b, "c" : c}
    return data

def filter_coordinates(coordinates, tem_height, tem_width):
    filter_coordinates = []

    if len(coordinates) !=0:
        filter_coordinates.append(coordinates[0])

    for i in range(0,len(coordinates)-1):
        if (abs(coordinates[i][0] - coordinates[i+1][0]) < tem_height/2 and abs(coordinates[i][1] - coordinates[i+1][1]) < tem_width/2) == False:
            filter_coordinates.append(coordinates[i+1])
    return filter_coordinates



def save_results(coordinates, template, template_name, rs_directory):
    results = {}
    results["coordinates"] = sorted(coordinates, key=lambda x: x[0])
    results["templat_size"] = (len(template), len(template[0]))
    with open(os.path.join(rs_directory, template_name), "w") as file:
        json.dump(results, file)


def main():
    args = parse_args()
    img = read_image(args.img_path)
    template = read_image(args.template_path)
    coordinates = detect(img, template)
    template_name = "{}.json".format(os.path.splitext(os.path.split(args.template_path)[1])[0])    
    save_results(coordinates, template, template_name, args.rs_directory)


if __name__ == "__main__":
    main()
