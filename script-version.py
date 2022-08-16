# %%
from operator import ge
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build # pip3 install --upgrade google-api-python-client
import pytube # pip install pytube
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from os.path import exists
from os import makedirs
from urllib.request import urlretrieve

DOWNLOAD_PATH = r'\songs-hrithvik'

# %%
# use spotify api to collect the urls of all the albums
def get_all_albums_helper(results, albums):
    for item in results['items']:
        album = item['album']
        albums.append(album)

def get_all_albums(sp):
    albums = list()
    
    results = sp.current_user_saved_albums()
    get_all_albums_helper(results, albums)

    while results['next']:
        results = sp.next(results)
        get_all_albums_helper(results, albums)

    return albums

# %%
# using name of song find the link
def find_song_link(name, author):
    return pytube.Search(author + ' - ' + name).results[0]

# %%
# use youtube api to download the song at some link to a given path
def download_video(path, link):
    try:
        yt = pytube.YouTube(link)
        print(f'Downloading {yt.title} by {yt.author}...')

        yt.streams.filter(only_audio=True).first().download(path)
    except:
        print('Could not connect, try again.')

# %%
def remove_illegal_chars(folder_name):
    for illegal_char in list('#%:{}\\/<>*?$!\'"@+`|='):
        folder_name = folder_name.replace(illegal_char, '')
    
    return folder_name

# %%
# spotify api stuff
id = 'ff1b9dbff35a46f3b96b026bc3f36aaa'
secret = '224f04a3e7d34b11b0d45c3165bf02b2'
uri = 'http://localhost:8080/callback/'
scope = 'user-library-read'

auth_manager = SpotifyOAuth(client_id=id, client_secret=secret, redirect_uri=uri, scope=scope, username='hrithvikambari')

sp = Spotify(auth_manager=auth_manager)
albums = get_all_albums(sp)
# %%
# build youtube api obj w/ api key
youtube = build("youtube", "v3", developerKey = "AIzaSyB_j2X58inzzGpDrVFpsHZPKrzQSYOKPqI")

# %%
print(len(albums))

# %%
for album in albums:
    download_list = list()
    temp_path = DOWNLOAD_PATH + r"\\" + remove_illegal_chars(album['name'])
    
    if (exists(temp_path)):
        print('Album: ', album['name'], ' already exists')
    else:
        print('Album: ', album['name'], ' downloading now...')
        album_len = len(album['tracks']['items'])
        while (len(download_list) != album_len):
            for track in album['tracks']['items']:
                track_name = track['name']
                artist_name = album['artists'][0]['name']
                link = find_song_link(track_name, artist_name)

                try:
                    download_list.append(link.streams.filter(only_audio=True).first())
                    print('\tadded ', track_name, ' by ', artist_name , ' to the download list')
                except:
                    # do nothing i guess
                    print('lol error')
                    album_len -= 1
        
        print('\n\tdownloading from download list to ', temp_path)
        for song in download_list:
            song.download(temp_path)


