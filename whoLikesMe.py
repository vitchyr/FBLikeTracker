# See http://docs.python.org/2/library/urllib.html#examples
import os, json, sys, operator, urllib, re
import facebook
from pprint import pprint

def process_pictures(graph, user_name):
    data_type = "Picture"

    # Individual Albums
    all_pictures_dataset = get_albums_like_dataset(graph)
    for album_name, data in all_pictures_dataset.items():
        save_data(user_name, album_name, data_type, data)

    # Pictures of me
    pictures_of_me_data = graph.get_connections("me", "photos", limit=0)['data']
    pictures_of_me_likes = get_likes_data(pictures_of_me_data)
    save_data(user_name, "Pictures of Me", data_type, pictures_of_me_likes)
    all_pictures_dataset["Pictures of Me"] = pictures_of_me_likes

    # All pictures
    all_pictures = combine_results(all_pictures_dataset)
    save_data(user_name, "All Pictures", data_type, all_pictures)

def get_albums_like_dataset(graph):
    albums = graph.get_connections("me", "albums")['data']

    album_like_dataset = {}

    for album in albums:
        album_data = graph.get_connections(album['id'], "photos", limit=0)['data']
        album_like_dataset[album['name']] = get_likes_data(album_data)

    return album_like_dataset

# Merges different like datas into one data
def combine_results(data_set):
    combined_data = {}

    for data in data_set.values():
        for name, likes in data.items():
            if name in combined_data:
                combined_data[name] += likes
            else:
                combined_data[name] = likes

    return combined_data

def process_statuses(graph, user_name):
    statuses_data = graph.get_connections("me", "statuses", limit=0)['data']
    statuses_likes = get_likes_data(statuses_data)
    save_data(user_name, "Statuses", "Status", statuses_likes)

# Returns the like data of an object, which is just a dictionary.
# The key is the user name. The value is an int
# of the amount of times that user has like your object.
def get_likes_data(data):
    like_data = {}
    
    for datum in data:
        if 'likes' not in datum:
            continue

        likes = datum['likes']['data']

        for like in likes:
            name = like['name']
        
            if name in like_data:
                like_data[name] += 1
            else:
                like_data[name] = 1

    
    return like_data
    
# raw_user_name: name of user whos data is being saved
# raw_data_name: name of objects being saved (e.g. "Profile Pictures", "Recent Statuses")
# raw_data_type: name of type of object being saved (e.g. "pictures", "statuses")
# data: the data to save
def save_data(user_name, data_name, data_type, data):
    # Get extra information
    ff_user_name = file_friendly(user_name)
    ff_data_name = file_friendly(data_name)
    ff_data_type = file_friendly(data_type)

    sorted_data = sorted(data.iteritems(), key=operator.itemgetter(1), reverse=True)

    num_likes = 0
    for tuple in sorted_data:
        num_likes += tuple[1]

    num_likers = len(sorted_data)

    # Prepare directory/fileto save data
    out_dir = 'output/{0}/{1}'.format(ff_user_name, ff_data_type)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    f = open('{0}/{1}_likes.dat'.format(out_dir, ff_data_name),'w')

    # Save data
    f.write("{0} Like Data of: {1}\nSource: {2}\nNumber of Likes: {3}\nNumber of Likers: {4}\n\n".format(data_type, user_name, data_name, num_likes, num_likers))

    f.write("User Name\tLikes\n")
    for tuple in sorted_data:
        f.write("{0}\t{1}\n".format(tuple[0].encode('utf-8'), tuple[1]))
        
    f.close()

# Replace white spaces with underscores and only keeps alphanumeric characters
def file_friendly(s):
    s = re.sub('[\ ]', '_', s)
    return re.sub('[^A-Za-z0-9_]+', '', s)
    
if __name__ == "__main__":
    oauth_access_token = "CAACEdEose0cBAC0Yywbql7A9IqVz2VNzgXceZBbvKmLmKDJyKJqluOb2SKAEtPTwZBLUsBAlxowiZCDB4z8pUO5wffltxyjxNthZBM5jKT3K0nX3SmkmuXYdOm1v2MzdZC8MUJMWAmgbs8O6Pak86nC48wdJDgjqzuqZCffHVZAawZDZD"
    
    graph = facebook.GraphAPI(oauth_access_token)
    user_name = graph.get_object("me")['name']
    
    process_pictures(graph, user_name)
    process_statuses(graph, user_name)