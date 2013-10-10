# See http://docs.python.org/2/library/urllib.html#examples
import json, sys, operator, urllib
from pprint import pprint

def get_fql_query_results(query_string, access_token = None):
	query = urllib.quote(query_string)
	
	if access_token is not None:
		query += "&access_token=" + access_token

	url = "https://graph.facebook.com/fql?q=" + query
	
	return json.loads(urllib.urlopen(url).read())
	
def get_id_name_map(user_id, access_token):
	q = "SELECT name, uid FROM user WHERE uid IN(SELECT uid1 FROM friend WHERE uid2 = {0})".format(user_id)
	
	raw_data = get_fql_query_results(q, access_token)
	
	names = {}
	
	for user in raw_data["data"]:
		user_id = user["uid"]
		if user_id not in names:
			names[user_id] = user["name"]

	return names

def get_photo_like_users(user_id, access_token):
	# to get profile pictures:
	q = "SELECT user_id FROM like WHERE object_id IN (SELECT object_id FROM photo WHERE aid IN (SELECT aid FROM album WHERE name = \'Profile Pictures\' AND owner = {0}) )".format(user_id)
	
	like_users = get_fql_query_results(q, access_token)
	
	return like_users["data"]

# Returns a dictionary with photo like data.
# The key is the user name. The value is an int
# of the amount of times that user has like your photo.
def get_profile_picture_like_data(user_id, access_token):
	users = get_photo_like_users(user_id, access_token)
	
	id_name_map = get_id_name_map(user_id, access_token)
	
	results = {}
	
	for user in users:
		id = user['user_id']

		# get name
		if id in id_name_map:
			name = id_name_map[id]
		else:
			name = "Not a friend. Id {0}".format(id)
		
		# record liker
		if name in results:
			results[name] += 1
		else:
			results[name] = 1
	
	return results
	
def print_results(results, user_id):
	sorted_results = sorted(results.iteritems(), key=operator.itemgetter(1), reverse=True)

	file_name = '{0}_output.dat'.format(user_id)
	
	f = open(file_name,'w')

	for tuple in sorted_results:
		f.write("{0}\t{1}\n".format(tuple[0].encode('utf-8'), tuple[1]))
		
	f.close()
	
if __name__ == "__main__":
	user_id = 1314024591
	
	access_token = "CAACEdEose0cBAHCvqiCDZC1PX0eHO9Kv8LJfuiY1ZA227fzZA9LVzcI7pvEcAgH12zu4veAJeGhsggimUqSjDZCTqfNFo1FC4VZCeo67ZBKf9xkjXhvVQekVD4OKu6EgHTddohzpJqyM9tr4YAo6d2aKZBjnxYekEJnT7huPQ4dawZDZD"
	
	like_data = get_profile_picture_like_data(user_id, access_token)
		
	print_results(like_data, user_id)
	