import requests
import hashlib
import time
import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import webbrowser

API_KEY = 'apikey'
API_SECRET = 'apisecret'
SESSION_FILE = 'lastfm_sessions.json'

class LastFMScrobbler:
    def __init__(self, master):
        self.master = master
        master.title("Last.fm Scrobbler")

        self.label_account = tk.Label(master, text="choose account:")
        self.label_account.pack()

        self.accounts = self.load_accounts()
        self.selected_account = tk.StringVar()
        self.dropdown = ttk.Combobox(master, textvariable=self.selected_account, state="readonly")
        self.dropdown['values'] = list(self.accounts.keys())
        self.dropdown.pack()

        self.label_artist = tk.Label(master, text="artist :")
        self.label_artist.pack()
        self.entry_artist = tk.Entry(master)
        self.entry_artist.pack()

        self.label_track = tk.Label(master, text="track:")
        self.label_track.pack()
        self.entry_track = tk.Entry(master)
        self.entry_track.pack()

        self.label_album = tk.Label(master, text="album:")
        self.label_album.pack()
        self.entry_album = tk.Entry(master)
        self.entry_album.pack()

        self.button_scrobble = tk.Button(master, text="add scrobble", command=self.add_scrobble)
        self.button_scrobble.pack()

        self.button_auth = tk.Button(master, text="add new account", command=self.open_auth_window)
        self.button_auth.pack()

    def save_session_key(self, username, session_key):
        self.accounts[username] = session_key
        with open(SESSION_FILE, 'w') as f:
            json.dump(self.accounts, f)

        self.dropdown['values'] = list(self.accounts.keys())

    def load_accounts(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        return {}

    def get_session_key(self, token):
        api_sig = hashlib.md5(f'api_key{API_KEY}methodauth.getSessiontoken{token}{API_SECRET}'.encode('utf-8')).hexdigest()
        url = 'https://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'auth.getSession',
            'token': token,
            'api_key': API_KEY,
            'api_sig': api_sig,
            'format': 'json'
        }
        response = requests.get(url, params=params)
        return response.json()

    def scrobble_track(self, session_key, artist, track, album, timestamp):
        api_sig = hashlib.md5(f'album{album}api_key{API_KEY}artist{artist}methodtrack.scrobblesk{session_key}timestamp{timestamp}track{track}{API_SECRET}'.encode('utf-8')).hexdigest()
        url = 'https://ws.audioscrobbler.com/2.0/'
        params = {
            'method': 'track.scrobble',
            'artist': artist,
            'track': track,
            'album': album,
            'timestamp': timestamp,
            'api_key': API_KEY,
            'api_sig': api_sig,
            'sk': session_key,
            'format': 'json'
        }
        response = requests.post(url, data=params)
        return response.json()

    def open_auth_window(self):
        webbrowser.open(f"https://last.fm/api/auth?api_key={API_KEY}")

        auth_window = tk.Toplevel(self.master)
        auth_window.title("add account")

        label_token = tk.Label(auth_window, text="enter token:")
        label_token.pack()

        entry_token = tk.Entry(auth_window)
        entry_token.pack()

        button_submit = tk.Button(auth_window, text="save token", command=lambda: self.authenticate_user(entry_token.get(), auth_window))
        button_submit.pack()

        auth_window.transient(self.master)

    def authenticate_user(self, token, auth_window):
        if not token:
            messagebox.showerror("error", "Token empty! err498")
            return

        session_data = self.get_session_key(token)
        if 'session' in session_data:
            session_key = session_data['session']['key']
            username = session_data['session']['name']
            self.save_session_key(username, session_key)
            messagebox.showinfo("success", f"account {username} added!")
            auth_window.destroy()
        else:
            messagebox.showerror("error", f"error occurred: {session_data.get('message', 'err404')}")

    def add_scrobble(self):
        selected_username = self.selected_account.get()
        session_key = self.accounts.get(selected_username)

        if not session_key:
            messagebox.showerror("error", "select an account or add a new one. err428")
            return

        artist = self.entry_artist.get()
        track = self.entry_track.get()
        album = self.entry_album.get()
        timestamp = int(time.time())

        result = self.scrobble_track(session_key, artist, track, album, timestamp)

        if 'scrobbles' in result:
            messagebox.showinfo("success", "Scrobble has been added!")
        else:
            messagebox.showerror("error", f"error occurred: {result}")

def main():
    root = tk.Tk()
    app = LastFMScrobbler(root)
    root.mainloop()

if __name__ == "__main__":
    main()
