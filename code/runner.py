"""
Module defines functions and main program to execute face match algorithm.
"""

from RekognitionAPI import *
from Helper import *
import glob
import itertools

def one_in_image(image,count,face_to_match):
    """
    If only one face is detected in a photo, this function will try to identify it.

    Either the face is detected, or it's gender is used to reduce the pool of
    source images to match it against with.

    Parameter image: image to recognize face in
    Parameter count: number of faces left to detect
    Parameter: information regarding face to recognize (gender,pose)
    """
    recognized = clean_list(rekognitionAPI.recognize(image),astronaut_data)
    count -= len(recognized) # len(recognized) = 0 if no match
    if count != 0: # if still not match, then reduce pool instead
        gender = face_to_match[0][0]
        pool = subset_gender(gender,astronaut_data)
        pool_subset = pool
    else: # otherwise, store recognized astronaut's name
        for name in recognized:
            match_dictionary[id].append(name)
    return count,recognized

def multiple_in_image(image,count):
    """
    If only multiple faces are detected in a photo, this function will try
    to identify them all.

    Either all faces are detected, or only some are or none. In case of some,
    use historical flight mission dates to reduce pool of possible source images.

    Parameter image: image to recognize face in
    Parameter count: number of faces left to detect
    """
    hd = setup_date_data() # for querying the date data
    recognized = clean_list(rekognitionAPI.recognize(image),astronaut_data)
    count -= len(recognized)
    if count != 0: # if none or few matched, reduce pool
        for astro in recognized:
            x = history_dictionary[astro]
            hd = eval(setup_date_query(x))
        pool = list(set(hd.name)) # add name to pool
        pool_subset = pool
    for name in recognized: # for those recognized, add to final matches
        match_dictionary[id].append(name)
    return count,recognized

def leftovers(image,count,recognized):
    """
    Leftover unmatched images need to be compared with source faces one by one.

    In this case, subset_pool is used if it exists, otherwise, for each unmatched
    face, check it against a set of 240 faces from source folder. Reducing the pool
    reduces the set from 240 to 11 on average.

    Parameter image: image to recognize faces in
    Parameter count: number of faces left to detect
    Parameter recognized: if some faces were recognized
    """
    for source in sources: # for each source, extract name and compare
        source_name = source.split("\\")[-1][:-4]
        if source_name.replace("_"," ") in recognized: # if source is already found, skip
            continue
        # if source is not in subset_pool (based on gender, or flight dates) skip
        if len(pool_subset) > 0 and source_name.replace("_"," ") not in pool_subset:
            continue
        face_matches=rekognitionAPI.compare_faces(source, image)
        if face_matches > 0: # if face matches, returns count of matches
            match_dictionary[id].append(source_name.replace("_"," "))
            count-=1
        if count == 0:
            break

def find_matches(image):
    """
    Function that drives the face identification setup.

    For a given image, first check if a face is detected. If one detected, see
    if it can be recognized. If not recognized, then subset source pool using gender
    instead. If multiple detected, check if some or all can be recognized. If
    not recongized, then have to compare each face with a source face. If some
    are recognized, then reduce the source pool using flight date information.

    Parameter image: image to recognize faces in
    """
    id = image.split("/")[-1][:-4] # image ID
    match_dictionary[id] = [] # global dictionary
    recognized = [] # matches from API
    faces_to_match = rekognitionAPI.detect_faces(image) # how many to match
    if faces_to_match == -1: # error, skip image
        return
    how_many = len(faces_to_match)
    if how_many == 1:
        how_many,recognized=one_in_image(image,how_many,faces_to_match)
    elif how_many > 1:
        how_many,recognized=multiple_in_image(image,how_many)
    if how_many > 0:
        leftovers(image,how_many,recognized)
    #write list of information for image to file
    with open("../data/matches.txt","a") as outfile:
        print(id,",".join(match_dictionary[id]),sep="|",file=outfile)


def generate_pairs():
    """
    Function uses matches to create pairs of astronauts that were photographed
    together for network graphs.

    If more than 1 astronaut is detected in a photograph, all possible pairs are
    generated and are written to file.
    """
    with open("../data/matches.txt",encoding="utf-8") as infile:
        matches = infile.readlines()
    matches = [i.strip().split("|")[2] for i in matches] # only store matched data
    matches = [i for i in matches if i!=""] # only keep when matched
    outfile = open("../data/pairs.txt","w",encoding="utf-8")
    for match in matches:
        match = match.split(",")
        if len(match) > 1: # if more than 1 were identified in a photograph
            for pair in itertools.combinations(match,2): # generate pairs of 2
                a = pair[0]
                b = pair[1]
                print(a,b,astronaut_dictionary[a],astronaut_dictionary[b],sep=",",file=outfile)
    outfile.close()


rekognitionAPI = RekognitionAPI() # API object
astronaut_data,astronaut_dictionary= fetch_astronaut_info() # gender data
history_dictionary = fetch_history_dictionary() # flight dates dictionary

images = glob.glob("../images/flickr/*") # images
sources = glob.glob("../images/source/*") # source images
match_dictionary = {} # global variable for matches
pool_subset = [] # global variable for source pool subsets

# for each image, find matches, write to file, then generate pairs file
for image in images:
   find_matches(image)
generate_pairs()
