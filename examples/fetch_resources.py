from filebrowserclient import FileBrowserClient, Forbidden

BASE_URL = "https://fileserver.com/"
USERNAME = "username"
PASSWORD = "password"

try:
    client = FileBrowserClient(BASE_URL).with_auth(USERNAME, PASSWORD)
except Forbidden:
    print("username or password is incorrect")
    exit(1)

with client:
    resources = client.list_resources()
    print(resources.name)
    for item in resources.items:
        print(resources.name, resources.type)
