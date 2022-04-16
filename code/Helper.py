"""
Module defines helper functions used across the project.
"""
import pandas as pd

def fetch_astronaut_info():
    """
    Generate astronaut name,gender,etc. data from csv file, and return a list and
    a dictionary based on that. Dictionary maps astronaut name to their agency.

    The data is used to match for correct astronaut spelling of names, and for
    subsetting match pool based on gender.
    """

    with open("../data/astronaut-data.csv","r",encoding="utf-8") as file:
        file.readline() # skip first line as it lists columns
        astronaut_data = file.readlines()
    astronaut_data = [i.strip().split(",") for i in astronaut_data] # convert to list of lists
    astronaut_dictionary = {}
    for i in astronaut_data:
        astronaut_dictionary[i[1]] = i[4]
    return astronaut_data,astronaut_dictionary


def fetch_history_dictionary():
    """
    Generate astronaut flight history as a dictionary.

    Rekognition API results can have different spelling for astronaut, match with
    the right astronaut and also provide country and gender information.
    """
    with open("../data/astronaut-history.csv","r",encoding="utf-8") as file:
        file.readline()
        history = file.readlines()
    history_dictionary = {}
    history = [i.strip().split(",") for i in history]
    for i in history: # i[1] in file is name spelling used across project
        if i[1] in history_dictionary:
            history_dictionary[i[1]].append((i[3],i[4]))
        else:
            history_dictionary[i[1]] = [(i[3],i[4])]
    return history_dictionary


def setup_date_data():
    """
    Generate astronaut flight history as a data frame for querying.

    data contains flight up and down dates, used to reduce pool of astronauts.
    """
    data = pd.read_csv("../data/astronaut-history.csv",encoding="utf-8")
    data['inDate'] = pd.to_datetime(data['in'])
    data['outDate'] = pd.to_datetime(data['out'])
    return data

def setup_date_query(hist):
    """
    Generate query to check for all astronauts that were present on the space
    station during a particular date range.

    This helps reduce the pool of astronauts to compare at the end.

    Parameter hist: list of mission up and down dates for set of astronauts
    """
    query = "hd["
    for i in hist:
        ins = pd.to_datetime(i[0])
        outs = pd.to_datetime(i[1])
        # query: either A is between the times of B, or A arrived before B, or B arrived before A left
        query+=" (hd['inDate'] <= '{}') & (hd['inDate'] <= hd['outDate']) & ('{}' <= hd['outDate']) & ('{}' <= '{}') ".format(outs,ins,ins,outs)
        query+=" |"
    query=query[:-1]+"]"
    return query

def subset_gender(type,astronaut_data):
    """
    Generate a list of all astronauts that match a gender value for a given astronaut

    This helps reduce the pool of astronauts to compare at the end.

    Parameter type: Gender value
    Parameter astronaut_data: data set to query to find possible matches
    """
    if type == 'NA':
        possible_matches = [i for i in astronaut_data]
    elif type == 'Male':
        possible_matches = [i for i in astronaut_data if i[5] == 'Male']
    elif type == 'Female':
        possible_matches = [i for i in astronaut_data if i[5] == 'Female']
    return possible_matches


def clean_list(names,lst):
    """
    Function finds the correct spelling of astronauts after getting results from
    Rekognition API call.

    Parameter names: list of names
    Parameter lst: list to check for correct spelling (always astronaut_data)
    """
    matches = []
    for name in names:
        for record in lst:
            if name in ",".join(record): # check if name matches any spelling
                matches.append(record[1]) # if it does, add to matches and stop
                break
    return matches
