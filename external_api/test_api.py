
import requests

#JSONPlaceholder 
url = "https://jsonplaceholder.typicode.com/posts"


print("Making GET request to:", url)
response = requests.get(url)


print("Status Code:", response.status_code)


data = response.json()

print("Type of data received:", type(data))

if isinstance(data, list):
    print("Number of posts:", len(data))
    if len(data) > 0:
        print("First post title:", data[0]['title'])
        print("First post body preview:", data[0]['body'][:100], "...")