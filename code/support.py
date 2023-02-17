from csv import reader
from os import walk
import pygame

def import_csv_layout(path):

    terrain_map = []
    # open the file
    with open(path) as level_map:
        # returns an object containing numbers (as the csv file) :
        # example for boundary : 395 invisible block, -1 : nothing
        layout = reader(level_map, delimiter=',')
        
        # store each row of number as a list inside terrain_map, and return it
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

# getting every file in a folder
def import_folder(path):

    surfaces = []
    for _,__,img_files in walk(path):
        # * we do a _  then __ becuase walk returns a tuple containing the path, then a list of the names of the subfolders, and then a list of the names of the files inside the folder, which is what we care about.
        for image in img_files:
            # create a fullpath
            full_path = path + "/" + image
             
            # get the image corresponding to that path
            image_surf = pygame.image.load(full_path).convert_alpha()

            #add it to the surfaces
            surfaces.append(image_surf)
    
    return surfaces
