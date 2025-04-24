import os
import webbrowser
import subprocess
import re
import urllib.parse
import json
from pathlib import Path

def play_spotify_song(song_name, artist_name=None):
    """Play a specific song on Spotify"""
    try:
        # Try to open Spotify desktop app
        spotify_path = "C:\\Users\\prajw\\AppData\\Roaming\\Spotify\\Spotify.exe"
        
        if os.path.exists(spotify_path):
            # Construct the Spotify URI for the search
            query = song_name
            if artist_name:
                query += f" artist:{artist_name}"
            
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            
            # Construct the Spotify URI
            spotify_uri = f"spotify:search:{encoded_query}"
            
            # Open Spotify with the search URI
            subprocess.Popen([spotify_path, spotify_uri])
            
            if artist_name:
                return f"Searching for '{song_name}' by {artist_name} on Spotify."
            else:
                return f"Searching for '{song_name}' on Spotify."
        else:
            # If desktop app not found, open Spotify Web
            if artist_name:
                query = f"{song_name} {artist_name}"
            else:
                query = song_name
                
            encoded_query = urllib.parse.quote(query)
            spotify_web_url = f"https://open.spotify.com/search/{encoded_query}"
            
            webbrowser.open(spotify_web_url)
            
            if artist_name:
                return f"Searching for '{song_name}' by {artist_name} on Spotify Web."
            else:
                return f"Searching for '{song_name}' on Spotify Web."
    except Exception as e:
        print(f"Error playing Spotify song: {e}")
        return play_youtube_music(song_name, artist_name)

def play_youtube_music(song_name, artist_name=None):
    """Play a specific song on YouTube Music"""
    try:
        # Construct the search query
        if artist_name:
            query = f"{song_name} {artist_name}"
        else:
            query = song_name
            
        # URL encode the query
        encoded_query = urllib.parse.quote(query)
        
        # Construct the YouTube Music URL
        youtube_music_url = f"https://music.youtube.com/search?q={encoded_query}"
        
        # Open YouTube Music in the browser
        webbrowser.open(youtube_music_url)
        
        if artist_name:
            return f"Searching for '{song_name}' by {artist_name} on YouTube Music."
        else:
            return f"Searching for '{song_name}' on YouTube Music."
    except Exception as e:
        print(f"Error playing YouTube Music: {e}")
        return f"Could not play '{song_name}'. Please try again."

def play_music(query):
    """Parse the query and play music accordingly"""
    # Extract song and artist information from the query
    song_pattern = r"play\s+(?:the\s+song\s+)?['\"]?([^'\"]+)['\"]?"
    artist_pattern = r"by\s+([^,\.]+)"
    
    song_match = re.search(song_pattern, query, re.IGNORECASE)
    artist_match = re.search(artist_pattern, query, re.IGNORECASE)
    
    if song_match:
        song_name = song_match.group(1).strip()
        artist_name = artist_match.group(1).strip() if artist_match else None
        
        # Try Spotify first, then fall back to YouTube Music
        return play_spotify_song(song_name, artist_name)
    else:
        # If no specific song is mentioned, just open the music app
        try:
            # Try to open Spotify
            spotify_path = "C:\\Users\\prajw\\AppData\\Roaming\\Spotify\\Spotify.exe"
            
            if os.path.exists(spotify_path):
                os.startfile(spotify_path)
                return "Opening Spotify."
            else:
                # If Spotify not found, open YouTube Music
                webbrowser.open("https://music.youtube.com")
                return "Opening YouTube Music."
        except Exception as e:
            print(f"Error opening music app: {e}")
            webbrowser.open("https://music.youtube.com")
            return "Opening YouTube Music."