import os
import sys
import webbrowser
import tempfile
import colorsys
import base64
import json
import tkinter as tk
import customtkinter as ctk


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)

    if not os.path.exists(path) and hasattr(sys, '_MEIPASS'):
        path = os.path.join(sys._MEIPASS, relative_path)

    return path


class BobHub(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("BobHub")
        self.geometry("1100x700")
        self.configure(fg_color="#121212")

        self.hue = 0.0
        self.jogos = []
        self.best_games = []
        self.favoritos = self.carregar_favoritos()
        self.cards = []
        self.favoritos_nomes = {j["nome"] for j in self.favoritos}

        self.header = ctk.CTkFrame(self, fg_color="#121212")
        self.header.pack(fill="x", pady=10)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="🎮 BobHub",
            font=("Segoe UI", 28, "bold")
        )
        self.title_label.pack()

        self.yt_btn = ctk.CTkButton(
            self.header,
            text="▶ YouTube",
            width=140,
            fg_color="#cc0000",
            hover_color="#ff0000",
            text_color="white",
            command=lambda: webbrowser.open("https://www.youtube.com/@BobDevelopercup")
        )
        self.yt_btn.pack(pady=5)

        self.subtitle = ctk.CTkLabel(
            self.header,
            text="HackedGames / OfflineGames",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        self.subtitle.pack(pady=5)

        self.search = ctk.CTkEntry(
            self,
            placeholder_text="Pesquisar jogos...",
            width=400
        )
        self.search.pack(pady=10)
        self.search.bind("<KeyRelease>", self.filtrar_jogos)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=1000,
            height=550,
            fg_color="#121212"
        )
        self.scroll_frame.pack(pady=10, expand=True, fill="both")

        self.carregar_jogos()
        self.renderizar()
        self.animar_rgb()

    def carregar_favoritos(self):
        if os.path.exists("favoritos.json"):
            try:
                with open("favoritos.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def salvar_favoritos(self):
        try:
            with open("favoritos.json", "w", encoding="utf-8") as f:
                json.dump(self.favoritos, f, indent=4)
        except IOError:
            pass

    def limpar_nome(self, nome):
        return nome.replace("-Online", "").replace("_Online", "").strip()

    def jogo_online(self, nome):
        return "-Online" in nome or "_Online" in nome

    def toggle_favorito(self, jogo):
        nome = jogo["nome"]

        if nome in self.favoritos_nomes:
            self.favoritos = [j for j in self.favoritos if j["nome"] != nome]
            self.favoritos_nomes.remove(nome)
        else:
            self.favoritos.append({
                "nome": nome,
                "path": jogo.get("path", ""),
                "data": jogo.get("data", None)
            })
            self.favoritos_nomes.add(nome)

        self.salvar_favoritos()
        self.renderizar()

    def animar_rgb(self):
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        color = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
        self.subtitle.configure(text_color=color)

        self.hue = (self.hue + 0.01) % 1.0
        self.after(50, self.animar_rgb)

    def carregar_jogos(self):
        pasta_best = get_resource_path(os.path.join("SystemBobHub", "BestGames"))
        if os.path.exists(pasta_best):
            self.best_games = [
                {"nome": os.path.splitext(f)[0], "path": os.path.join(pasta_best, f)}
                for f in os.listdir(pasta_best) if f.endswith(".html")
            ]

        pasta = get_resource_path("SystemBobHub")
        if os.path.exists(pasta):
            self.jogos = [
                {"nome": os.path.splitext(f)[0], "path": os.path.join(pasta, f)}
                for f in os.listdir(pasta) if f.endswith(".html")
            ]

    def abrir_jogo(self, jogo):
        if "data" in jogo and jogo["data"]:
            try:
                data = jogo["data"]
                if "base64," in data:
                    data = data.split("base64,")[1]

                try:
                    html = base64.b64decode(data).decode("utf-8", errors="ignore")
                except Exception:
                    html = data

                with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp:
                    temp.write(html)
                    path = temp.name

                webbrowser.open(f"file://{os.path.abspath(path)}")
            except Exception:
                pass
        elif "path" in jogo and jogo["path"]:
            webbrowser.open(f"file://{os.path.abspath(jogo['path'])}")

    def criar_card(self, parent, jogo):
        nome_original = jogo.get("nome", "Sem Nome")
        online = self.jogo_online(nome_original)
        nome_limpo = self.limpar_nome(nome_original)

        frame = ctk.CTkFrame(parent, fg_color="#1e1e1e", corner_radius=12)
        frame.pack(pady=5, fill="x")

        btn = ctk.CTkButton(
            frame,
            text=nome_limpo,
            fg_color="#1e1e1e",
            hover_color="#333333",
            text_color="white",
            anchor="w",
            command=lambda: self.abrir_jogo(jogo)
        )
        btn.pack(side="left", fill="x", expand=True, padx=10, pady=8)

        if online:
            label = ctk.CTkLabel(
                frame,
                text="🌐 Requer internet",
                text_color="#4da3ff",
                font=("Segoe UI", 10)
            )
            label.pack(side="left", padx=10)

        is_fav = nome_original in self.favoritos_nomes
        fav_btn = ctk.CTkButton(
            frame,
            text="★" if is_fav else "☆",
            width=40,
            fg_color="#2a2a2a",
            hover_color="#444444",
            text_color="#A855F7" if is_fav else "white",
            command=lambda: self.toggle_favorito(jogo)
        )
        fav_btn.pack(side="right", padx=10)

        self.cards.append({
            "frame": frame,
            "nome_busca": nome_limpo.lower()
        })

    def filtrar_jogos(self, event=None):
        texto = self.search.get().lower().strip()

        for c in self.cards:
            if texto in c["nome_busca"]:
                c["frame"].pack(pady=5, fill="x")
            else:
                c["frame"].pack_forget()

    def renderizar(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.cards = []

        self.criar_secao("MELHORES JOGOS", self.best_games, "#FFD700")
        self.criar_secao("FAVORITOS", self.favoritos, "#A855F7")
        self.criar_secao("TODOS OS JOGOS", self.jogos, "white")

    def criar_secao(self, titulo, lista, cor):
        if not lista:
            return

        label = ctk.CTkLabel(
            self.scroll_frame,
            text=titulo,
            font=("Segoe UI", 16, "bold"),
            text_color=cor
        )
        label.pack(pady=10)

        for j in lista:
            self.criar_card(self.scroll_frame, j)


if __name__ == "__main__":
    app = BobHub()
    app.mainloop()
