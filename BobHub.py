import os
import sys
import webbrowser
import tempfile
import colorsys
import base64
import json
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class BobHub(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("BobHub")
        self.geometry("1100x700")
        self.configure(fg_color="#121212")

        pasta_base = get_resource_path("SystemBobHub")
        pasta_best = os.path.join(pasta_base, "BestGames")
        if not os.path.exists(pasta_base):
            os.makedirs(pasta_base)
        if not os.path.exists(pasta_best):
            os.makedirs(pasta_best)

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

        self.config_btn = ctk.CTkButton(
            self.header,
            text="⚙ Configurações",
            width=140,
            fg_color="#2b2b2b",
            hover_color="#444444",
            text_color="white",
            command=self.abrir_configuracoes
        )
        self.config_btn.pack(pady=5)

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
        path = get_resource_path("favoritos.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def salvar_favoritos(self):
        path = get_resource_path("favoritos.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.favoritos, f, indent=4)
        except IOError:
            pass

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

    def criar_card(self, parent, jogo):
        nome = jogo.get("nome", "Sem Nome")

        frame = ctk.CTkFrame(parent, fg_color="#1e1e1e", corner_radius=12)
        frame.pack(pady=5, fill="x")

        frame.grid_columnconfigure(0, weight=1)

        btn = ctk.CTkButton(
            frame,
            text=nome,
            fg_color="#1e1e1e",
            hover_color="#333333",
            text_color="white",
            anchor="w",
            command=lambda: self.abrir_jogo(jogo)
        )
        btn.grid(row=0, column=0, sticky="ew", padx=10, pady=8)

        is_fav = nome in self.favoritos_nomes
        fav_btn = ctk.CTkButton(
            frame,
            text="★" if is_fav else "☆",
            width=40,
            fg_color="#2a2a2a",
            hover_color="#444444",
            text_color="#A855F7" if is_fav else "white",
            command=lambda: self.toggle_favorito(jogo)
        )
        fav_btn.grid(row=0, column=1, sticky="e", padx=10, pady=8)

        self.cards.append({
            "frame": frame,
            "nome_busca": nome.lower()
        })

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

    def filtrar_jogos(self, event=None):
        texto = self.search.get().lower().strip()

        for c in self.cards:
            if texto in c["nome_busca"]:
                if not c["frame"].winfo_manager():
                    c["frame"].pack(pady=5, fill="x")
            else:
                if c["frame"].winfo_manager():
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

    def abrir_configuracoes(self):
        janela_config = ctk.CTkToplevel(self)
        janela_config.title("Configurações")
        janela_config.geometry("400x380")
        janela_config.configure(fg_color="#121212")
        janela_config.transient(self)
        janela_config.grab_set()
        janela_config.resizable(False, False)

        label = ctk.CTkLabel(
            janela_config,
            text="Configurações do BobHub",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        label.pack(pady=20)

        importar_btn = ctk.CTkButton(
            janela_config,
            text="📥 Importar Pacote (.packBob)",
            width=250,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="#A855F7",
            hover_color="#9333EA",
            text_color="white",
            command=self.importar_pack
        )
        importar_btn.pack(pady=10)

        exportar_btn = ctk.CTkButton(
            janela_config,
            text="📤 Exportar Dados (.packBob)",
            width=250,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            text_color="white",
            command=self.exportar_pack
        )
        exportar_btn.pack(pady=10)

        formatar_btn = ctk.CTkButton(
            janela_config,
            text="⚠️ Formatar Hub",
            width=250,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            text_color="white",
            command=self.confirmar_formatacao
        )
        formatar_btn.pack(pady=10)

    def confirmar_formatacao(self):
        if messagebox.askyesno("Confirmação 1/2", "Você tem certeza que deseja formatar o Hub?\nIsso apagará todos os jogos e favoritos!"):
            if messagebox.askyesno("Confirmação 2/2", "ESTA AÇÃO É IRREVERSÍVEL!\nTem certeza absoluta de que deseja deletar tudo permanentemente?"):
                self.executar_formatacao()

    def executar_formatacao(self):
        path_fav = get_resource_path("favoritos.json")
        if os.path.exists(path_fav):
            try:
                os.remove(path_fav)
            except Exception:
                pass

        self.favoritos = []
        self.favoritos_nomes = set()

        pasta_base = get_resource_path("SystemBobHub")
        if os.path.exists(pasta_base):
            for item in os.listdir(pasta_base):
                item_path = os.path.join(pasta_base, item)
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                except Exception:
                    pass

        pasta_best = os.path.join(pasta_base, "BestGames")
        if not os.path.exists(pasta_base):
            os.makedirs(pasta_base)
        if not os.path.exists(pasta_best):
            os.makedirs(pasta_best)

        self.carregar_jogos()
        self.renderizar()

    def importar_pack(self):
        caminho_pacote = filedialog.askopenfilename(
            filetypes=[("Pacote de Jogos BobHub", "*.packBob")]
        )
        if not caminho_pacote:
            return

        try:
            lista_arquivos = []
            with zipfile.ZipFile(caminho_pacote, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('.html'):
                        nome_arquivo = os.path.basename(file_info.filename)
                        if nome_arquivo:
                            lista_arquivos.append(file_info.filename)

            if not lista_arquivos:
                return

            self.abrir_preview_pack(caminho_pacote, lista_arquivos)
        except Exception:
            pass

    def abrir_preview_pack(self, caminho_pacote, lista_arquivos):
        janela_preview = ctk.CTkToplevel(self)
        janela_preview.title("Conteúdo do Pacote")
        janela_preview.geometry("500x550")
        janela_preview.configure(fg_color="#121212")
        janela_preview.transient(self)
        janela_preview.grab_set()

        label_info = ctk.CTkLabel(
            janela_preview,
            text="Selecione quais jogos deseja enviar para BestGames:",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        label_info.pack(pady=15)

        checkboxes_vars = []

        def alternar_todos():
            estado = valor_todos.get()
            for var in checkboxes_vars:
                var.set(estado)

        valor_todos = tk.IntVar(value=0)
        chk_todos = ctk.CTkCheckBox(
            janela_preview,
            text="Selecionar Todos",
            variable=valor_todos,
            command=alternar_todos,
            font=("Segoe UI", 12, "bold"),
            fg_color="#A855F7",
            hover_color="#9333EA"
        )
        chk_todos.pack(pady=10, anchor="w", padx=30)

        scroll_preview = ctk.CTkScrollableFrame(
            janela_preview,
            width=440,
            height=320,
            fg_color="#1e1e1e"
        )
        scroll_preview.pack(pady=10, fill="both", expand=True, padx=20)

        itens_selecao = []
        for arq in lista_arquivos:
            nome_limpo = os.path.splitext(os.path.basename(arq))[0]
            var_chk = tk.IntVar(value=0)
            checkboxes_vars.append(var_chk)

            frame_item = ctk.CTkFrame(scroll_preview, fg_color="#2a2a2a", corner_radius=6)
            frame_item.pack(fill="x", pady=4, padx=5)

            chk = ctk.CTkCheckBox(
                frame_item,
                text=nome_limpo,
                variable=var_chk,
                fg_color="#FFD700",
                hover_color="#B8860B",
                text_color="white"
            )
            chk.pack(side="left", padx=10, pady=6)

            itens_selecao.append((arq, var_chk))

        def processar_importacao():
            pasta_base = get_resource_path("SystemBobHub")
            pasta_best = os.path.join(pasta_base, "BestGames")

            if not os.path.exists(pasta_base):
                os.makedirs(pasta_base)
            if not os.path.exists(pasta_best):
                os.makedirs(pasta_best)

            try:
                with zipfile.ZipFile(caminho_pacote, 'r') as zip_ref:
                    for caminho_interno, var_best in itens_selecao:
                        nome_f = os.path.basename(caminho_interno)

                        caminho_normal = os.path.join(pasta_base, nome_f)
                        if not os.path.exists(caminho_normal):
                            with zip_ref.open(caminho_interno) as src, open(caminho_normal, 'wb') as dst:
                                dst.write(src.read())

                        if var_best.get() == 1:
                            caminho_best = os.path.join(pasta_best, nome_f)
                            if not os.path.exists(caminho_best):
                                with zip_ref.open(caminho_interno) as src, open(caminho_best, 'wb') as dst:
                                    dst.write(src.read())

                self.carregar_jogos()
                self.renderizar()
                janela_preview.destroy()
            except Exception:
                pass

        btn_importar = ctk.CTkButton(
            janela_preview,
            text="Importar",
            width=200,
            height=40,
            font=("Segoe UI", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            command=processar_importacao
        )
        btn_importar.pack(pady=15)

    def exportar_pack(self):
        arquivos_para_exportar = set()
        pasta_base = get_resource_path("SystemBobHub")
        if os.path.exists(pasta_base):
            for root, dirs, files in os.walk(pasta_base):
                for file in files:
                    if file.lower().endswith(('.html', '.htm')):
                        arquivos_para_exportar.add(os.path.join(root, file))

        if not arquivos_para_exportar:
            messagebox.showwarning("Aviso", "Nenhum jogo encontrado para exportar.")
            return

        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".packBob",
            filetypes=[("Pacote de Jogos BobHub", "*.packBob")]
        )
        if not caminho_salvar:
            return

        try:
            with zipfile.ZipFile(caminho_salvar, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                adicionados = set()
                for arq in arquivos_para_exportar:
                    nome_f = os.path.basename(arq)
                    if nome_f not in adicionados:
                        zip_ref.write(arq, nome_f)
                        adicionados.add(nome_f)
            messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")
        except Exception:
            pass


if __name__ == "__main__":
    app = BobHub()
    app.mainloop()
