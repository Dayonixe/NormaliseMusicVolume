import threading
import shutil
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.normalise import normalize_directory


class NormaliseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Normaliseur de musique")
        self.geometry("600x300")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Variables
        self.input_dir = ctk.StringVar()

        # Graphical user interface
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(self, text="🎵 Normaliseur de volume audio", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(15, 10))

        # Folder selector
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(padx=20, pady=(10, 0), fill="x")

        folder_entry = ctk.CTkEntry(folder_frame, textvariable=self.input_dir, placeholder_text="Chemin du dossier musique")
        folder_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)

        browse_button = ctk.CTkButton(folder_frame, text="Parcourir", command=self.browse_folder, width=100)
        browse_button.pack(side="right", padx=(0, 10))

        # Launch button
        start_button = ctk.CTkButton(self, text="Lancer la normalisation", command=self.start_normalization, fg_color="#2fa572")
        start_button.pack(pady=(15, 5))

        # Progress bar
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.pack(pady=(10, 5), padx=20, fill="x")
        self.progressbar.set(0)

        # Status area
        self.status_label = ctk.CTkLabel(self, text="En attente...", anchor="w")
        self.status_label.pack(pady=(5, 5))

    # Actions

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Choisir le dossier de musique")
        if folder:
            self.input_dir.set(folder)

    def start_normalization(self):
        input_dir = self.input_dir.get().strip()
        if not input_dir:
            messagebox.showwarning("Erreur", "Veuillez sélectionner un dossier de musique.")
            return

        # Run in a thread so as not to block the UI
        thread = threading.Thread(target=self.run_normalization, args=(input_dir,))
        thread.start()

    def run_normalization(self, input_dir):
        try:
            self.status_label.configure(text="Normalisation en cours...")
            self.progressbar.set(0)

            def update_progress(current, total):
                # Updated from the main thread
                progress = current / total
                self.progressbar.set(progress)
                self.status_label.configure(text=f"Fichier {current}/{total} traité")

            # Step 1: Normalisation
            normalize_directory(
                input_dir=input_dir,
                output_dir=None,
                target_level=-16.0,
                progress_callback=update_progress
            )

            # Step 2: Clean & replace
            normalised_dir = os.path.join(input_dir, "_normalised")

            if os.path.isdir(normalised_dir):
                # Delete old audio files from the original folder
                for f in os.listdir(input_dir):
                    path = os.path.join(input_dir, f)
                    if os.path.isfile(path) and f.lower().endswith(('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac')):
                        os.remove(path)

                # Déplacer les nouveaux fichiers
                for f in os.listdir(normalised_dir):
                    src = os.path.join(normalised_dir, f)
                    dst = os.path.join(input_dir, f)
                    shutil.move(src, dst)

                # Delete the _normalised folder
                shutil.rmtree(normalised_dir, ignore_errors=True)

            self.status_label.configure(text="✅ Normalisation terminée !")
            messagebox.showinfo("Terminé", "Tous les fichiers ont été normalisés !")

        except Exception as e:
            self.status_label.configure(text="❌ Erreur")
            messagebox.showerror("Erreur", str(e))


if __name__ == "__main__":
    app = NormaliseApp()
    app.mainloop()