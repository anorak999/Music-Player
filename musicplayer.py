import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import os
from PIL import Image, ImageTk
import threading
import time

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("PyFlipper Music Player")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a1a')
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.current_song = None
        self.paused = False
        self.playlist = []
        self.current_index = 0
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create UI components
        self.create_playlist_frame()
        self.create_player_frame()
        self.create_controls_frame()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start playback thread
        self.playback_thread = None
        self.is_playing = False

    def create_playlist_frame(self):
        # Playlist frame
        playlist_frame = ttk.LabelFrame(self.main_frame, text="Playlist", padding=10)
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Playlist listbox
        self.playlist_box = tk.Listbox(playlist_frame, bg='#2a2a2a', fg='white',
                                     selectmode=tk.SINGLE, font=('Arial', 10))
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.playlist_box.bind('<<ListboxSelect>>', self.on_select_song)
        
        # Add songs button
        add_btn = ttk.Button(playlist_frame, text="Add Songs", command=self.add_songs)
        add_btn.pack(pady=5)

    def create_player_frame(self):
        # Player frame
        player_frame = ttk.LabelFrame(self.main_frame, text="Now Playing", padding=10)
        player_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Song info
        self.song_label = ttk.Label(player_frame, text="No song selected", font=('Arial', 12))
        self.song_label.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(player_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.progress_var, command=self.seek)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Time labels
        time_frame = ttk.Frame(player_frame)
        time_frame.pack(fill=tk.X)
        
        self.current_time = ttk.Label(time_frame, text="0:00")
        self.current_time.pack(side=tk.LEFT)
        
        self.total_time = ttk.Label(time_frame, text="0:00")
        self.total_time.pack(side=tk.RIGHT)

    def create_controls_frame(self):
        # Controls frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X)
        
        # Previous button
        self.prev_btn = ttk.Button(controls_frame, text="⏮", command=self.previous_song)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        # Play/Pause button
        self.play_btn = ttk.Button(controls_frame, text="▶", command=self.play_pause)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        # Next button
        self.next_btn = ttk.Button(controls_frame, text="⏭", command=self.next_song)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Volume control
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_scale = ttk.Scale(controls_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                                    variable=self.volume_var, command=self.set_volume)
        self.volume_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    def add_songs(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        for file in files:
            self.playlist.append(file)
        self.update_playlist()

    def update_playlist(self):
        self.playlist_box.delete(0, tk.END)
        for song in self.playlist:
            self.playlist_box.insert(tk.END, os.path.basename(song))

    def on_select_song(self, event):
        selection = self.playlist_box.curselection()
        if selection:
            self.current_index = selection[0]
            self.play_song()

    def play_song(self):
        if not self.playlist:
            return
            
        self.current_song = self.playlist[self.current_index]
        pygame.mixer.music.load(self.current_song)
        pygame.mixer.music.play()
        self.is_playing = True
        self.play_btn.configure(text="⏸")
        self.song_label.configure(text=os.path.basename(self.current_song))
        
        # Start playback thread
        if self.playback_thread is None or not self.playback_thread.is_alive():
            self.playback_thread = threading.Thread(target=self.update_progress)
            self.playback_thread.daemon = True
            self.playback_thread.start()

    def play_pause(self):
        if not self.current_song:
            return
            
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.configure(text="▶")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.play_btn.configure(text="⏸")

    def next_song(self):
        if not self.playlist:
            return
            
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_song()

    def previous_song(self):
        if not self.playlist:
            return
            
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_song()

    def seek(self, value):
        if not self.current_song:
            return
            
        try:
            pygame.mixer.music.set_pos(float(value) / 100 * pygame.mixer.Sound(self.current_song).get_length())
        except:
            pass

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def update_progress(self):
        while self.is_playing and pygame.mixer.music.get_busy():
            try:
                current_pos = pygame.mixer.music.get_pos() / 1000  # Convert to seconds
                total_length = pygame.mixer.Sound(self.current_song).get_length()
                
                # Update progress bar
                self.progress_var.set((current_pos / total_length) * 100)
                
                # Update time labels
                self.current_time.configure(text=self.format_time(current_pos))
                self.total_time.configure(text=self.format_time(total_length))
                
                time.sleep(0.1)
            except:
                break

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def on_closing(self):
        self.is_playing = False
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
