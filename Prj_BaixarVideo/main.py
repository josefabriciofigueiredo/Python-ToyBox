import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from threading import Thread, Lock
import os
import re
from typing import List, Dict, Any
import ssl
import certifi


class StyleEntry(tk.Entry):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["borderwidth"] = 0
        super().__init__(*args, **kwargs)
        separator = ttk.Separator(orient="horizontal")
        separator.place(in_=self, x=0, rely=1.0, height=2, relwidth=1.0)


class Template(tk.Tk):
    def __init__(self) -> None:
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(PagePrincipal)

        # Config
        self.title("Baixar Vídeos & Áudios")
        self.iconbitmap('./imgs/icone.ico')
        w = int(self.winfo_screenwidth() / 2 - 250)
        h = int(self.winfo_screenheight() / 2 - 200)
        self.geometry(f'500x400+{w}+{h}')
        self.resizable(False, False)

    def switch_frame(self, frame_class: type[tk.Frame]) -> None:
        new_frame = frame_class(self)

        if self._frame is not None:
            self._frame.destroy()

        self._frame = new_frame
        self._frame.place(x=0, y=0, width=500, height=400)


class PagePrincipal(tk.Frame):
    def __init__(self, master: Template) -> None:
        tk.Frame.__init__(self, master, bg='#2B2B2B')
        # Variáveis para Threads
        self.progressNum: tk.DoubleVar = tk.DoubleVar()
        self.active_threads: int = 0
        self.lock: Lock = Lock()

        # Variáveis
        self.imgDiretorioProcura: tk.PhotoImage = tk.PhotoImage(file='./imgs/pasta.png')
        video_url: tk.StringVar() = tk.StringVar()
        diretorio_url: tk.StringVar() = tk.StringVar()

        # Styles
        lbl_style: Dict[str, str] = {'font': 'Arial 10 bold', 'bg': '#2B2B2B', 'foreground': 'white'}
        btn_style: Dict[str, str] = {'font': 'Arial 10 bold', 'bg': '#4294FF', 'foreground': 'white', 'bd': 0,
                                     'disabledforeground': '#A4CBFF'}
        btnActive_style: Dict[str, str] = {'activebackground': '#6FADFF', 'activeforeground': 'white'}

        # Frame
        tk.Label(self, text='URLs dos Vídeos', **lbl_style).place(x=28, y=28, height=15)
        StyleEntry(self, textvariable=video_url,
                   font='Arial 10', foreground='white',
                   bg='#2B2B2B',
                   insertbackground='white').place(x=28, y=50, height=26, width=444)

        tk.Label(self, text='Local para Salvar', **lbl_style).place(x=28, y=95, height=15)
        StyleEntry(self, textvariable=diretorio_url,
                   font='Arial 10', foreground='white',
                   bg='#2B2B2B',
                   insertbackground='white').place(x=28, y=118, height=26, width=414)

        btn_Path = tk.Button(self, image=self.imgDiretorioProcura,
                             command=lambda: diretorio_url.set(filedialog.askdirectory()), bg='#2B2B2B', bd=0)
        btn_Path.place(x=446, y=118, height=26, width=26)
        btn_Path.configure(activebackground='#2B2B2B')

        self.btn_UploadVideo: tk.Button = tk.Button(self, text='Baixar Vídeo',
                                                    command=lambda: self.download('mp4', diretorio_url.get(),
                                                                                  video_url.get()), **btn_style)
        self.btn_UploadVideo.place(x=28, y=166, height=30, width=113)
        self.btn_UploadVideo.configure(**btnActive_style)

        self.btn_UploadAudio: tk.Button = tk.Button(self, text='Baixar Áudio',
                                                    command=lambda: self.download('mp3', diretorio_url.get(),
                                                                                  video_url.get()), **btn_style)
        self.btn_UploadAudio.place(x=157, y=166, height=30, width=113)
        self.btn_UploadAudio.configure(**btnActive_style)

    def download(self, type_extension: str, diretorio_path: str, video_urls: str) -> None:
        strUrls: str = video_urls.strip()
        strPath: str = diretorio_path.strip().replace("/", "\\")

        if strUrls == '' or strPath == '':
            messagebox.showinfo('Campo não preenchido!', 'Preencha os campos.')
        elif not os.path.exists(strPath):
            messagebox.showinfo('Diretório não existe!', 'Diretório informado não existe.')
        else:
            urls: List[str] = strUrls.split(' ')

            self.btn_UploadVideo.config(state='disabled')
            self.btn_UploadAudio.config(state='disabled')
            self.progressNum.set(0)

            progress_bar: ttk.Progressbar = ttk.Progressbar(self, variable=self.progressNum,
                                                            maximum=100,
                                                            mode='determinate')
            progress_bar.place(x=28, y=255, width=444)
            lbl_title: tk.Label = tk.Label(self, text=f'Baixando {len(urls)} ite{"ns" if len(urls) != 1 else "m"}...',
                                           font='Arial 10 bold',
                                           foreground='white',
                                           bg='#2B2B2B')
            lbl_title.place(x=28, y=230)

            list_box: tk.Listbox = tk.Listbox(self)
            list_box.place(x=28, y=280, width=444, height=90)

            def download_video(url_: str, index_: int, num_urls: int) -> None:
                def progress_callback(stream: Any, chunk: bytes, bytes_remaining: int) -> None:
                    total_size: int = stream.filesize
                    bytes_downloaded: int = total_size - bytes_remaining
                    percent_complete: int = int((bytes_downloaded / total_size) * 100)

                    list_box.delete(index_)
                    list_box.insert(index_, f"{percent_complete}% - '{title_file}'")
                    list_box.update_idletasks()

                try:
                    video: YouTube = YouTube(url_, on_progress_callback=progress_callback)
                    title_file: str = re.sub(r'[\\/:*?"<>|]', '_', video.title)[0:70]

                    list_box.insert(index_, "0% - '" + title_file + "'")

                    if type_extension == 'mp4':
                        video_stream: Any = video.streams.get_highest_resolution()

                        if video_stream:
                            video_stream.download(output_path=strPath, filename=f'{title_file}.mp4')
                        else:
                            messagebox.showinfo('Formato Invalido!', 'Não é um vídeo mp4:' + url_)
                    elif type_extension == 'mp3':
                        audio_stream: Any = video.streams.filter(only_audio=True).first()

                        if audio_stream:
                            audio_stream.download(output_path=strPath, filename=f'{title_file}.mp3')
                        else:
                            messagebox.showinfo('Formato Inválido!',
                                                'Não é possível encontrar uma stream de áudio para:' + url_)
                except RegexMatchError:
                    messagebox.showwarning('Erro!', f'URL não é válida: {url_}')
                except Exception as e:
                    messagebox.showwarning('Erro!', f'Erro: {e}')
                finally:
                    self.lock.acquire()
                    self.active_threads -= 1
                    self.lock.release()

                    self.progressNum.set(int((100 / num_urls) * (num_urls - self.active_threads)))
                    if self.active_threads == 0:
                        self.btn_UploadVideo.config(state='normal')
                        self.btn_UploadAudio.config(state='normal')

                        progress_bar.destroy()
                        lbl_title.destroy()
                        list_box.destroy()
                        self.update()

                        messagebox.showinfo('Sucesso!', 'Baixado com Sucesso')

            # Threads
            self.active_threads = len(urls)
            url_threads: List[Thread] = []
            for index, url in enumerate(urls):
                tarefa: Thread = Thread(target=download_video, args=(url, index, len(urls)))
                tarefa.start()
                url_threads.append(tarefa)


if __name__ == "__main__":
    # Configure SSL
    def configure_ssl() -> ssl.SSLContext:
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(certifi.where())
        return ssl_context

    ssl._create_default_https_context = configure_ssl

    # App
    app: Template = Template()
    app.mainloop()
