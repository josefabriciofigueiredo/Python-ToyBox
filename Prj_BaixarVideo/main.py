import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
import os
import re
import base64

# Imagen
img_path = b'iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAFOSURBVHgB7ZS7TgJREIb/f/ZCBIyGYG/hA9AILYmPoSbYovsMRl/AAqlFoom1jQ0asDK02voSWuESxl0TIxgOl+XQ8RW7c04m+2Vm5xxgRUK4E2gqp/1zAkVTkiob3bp7jQXgbvWrIsKrqYnUo5ea30BChKLbsyRGVdVLx71DJMSdIzcNSrN0EjanJarqbbfuHwzvCZYAyf3olxSWLopR4ebwemrrmCLoYG78LAvlmv7E7YDtiSIvL/DziYu++A32LrUy8SvuBmGDMMSnUSRpQrzFRaoYZBy0jK1zMnaqIfH4EPDDWJGzZkeEAe7j11gRvUiUtiPqEx2jyJZEB3h/DvhqFmUtnWNB6y8cJ7I0CNHE3RlFcdtooaCobWF8IxhFbtbStFE7w0shnbeRjXVLbSNvRrzxo1jtndKRspcjvK0EN+g/qGg/BTzDCht8A5unTIW7HHuEAAAAAElFTkSuQmCC'
img_icone = b'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'

if not os.path.exists('imgs'):
    os.mkdir('imgs')
if not os.path.exists('./imgs/pasta.png'):
    with open("imgs/pasta.png", "wb") as fh:
        fh.write(base64.decodebytes(img_path))
        fh.close()
if not os.path.exists('./imgs/icone.ico'):
    with open("imgs/icone.ico", "wb") as fh:
        fh.write(base64.decodebytes(img_icone))
        fh.close()


class StyleEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        kwargs["borderwidth"] = 0
        super().__init__(*args, **kwargs)
        separator = ttk.Separator(orient="horizontal")
        separator.place(in_=self, x=0, rely=1.0, height=2, relwidth=1.0)


class Template(tk.Tk):
    def __init__(self):
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

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)

        if self._frame is not None:
            self._frame.destroy()

        self._frame = new_frame
        self._frame.place(x=0, y=0, width=500, height=400)


class PagePrincipal(tk.Frame):
    def __init__(self, master):
        # Variáveis
        self.progressNum = tk.DoubleVar()
        self.video_url = tk.StringVar()
        self.diretorio_url = tk.StringVar()
        self.imgDiretorioProcura = tk.PhotoImage(file='./imgs/pasta.png')
        self.titleVideoBaixando = tk.StringVar()

        # Styles
        lbl_style = {'font': 'Arial 10 bold', 'bg': '#2B2B2B', 'foreground': 'white'}
        btn_style = {'font': 'Arial 10 bold', 'bg': '#4294FF', 'foreground': 'white', 'bd': 0}
        btnActive_style = {'activebackground': '#6FADFF', 'activeforeground': 'white'}

        # Frame
        tk.Frame.__init__(self, master, bg='#2B2B2B')

        tk.Label(self, text='URLs dos Vídeos', **lbl_style).place(x=28, y=28, height=15)
        StyleEntry(self, textvariable=self.video_url,
                   font='Arial 10', foreground='white',
                   bg='#2B2B2B',
                   insertbackground='white').place(x=28, y=50, height=26, width=444)

        tk.Label(self, text='Local para Salvar', **lbl_style).place(x=28, y=95, height=15)
        StyleEntry(self, textvariable=self.diretorio_url,
                   font='Arial 10', foreground='white',
                   bg='#2B2B2B',
                   insertbackground='white').place(x=28, y=118, height=26, width=414)

        btn_Path = tk.Button(self, image=self.imgDiretorioProcura, command=self.select_path, bg='#2B2B2B', bd=0)
        btn_Path.place(x=446, y=118, height=26, width=26)
        btn_Path.configure(activebackground='#2B2B2B')

        btn_UploadVideo = tk.Button(self, text='Baixar Vídeo', command=self.upload_video, **btn_style)
        btn_UploadVideo.place(x=28, y=166, height=30, width=113)
        btn_UploadVideo.configure(**btnActive_style)

        btn_UploadAudio = tk.Button(self, text='Baixar Áudio', command=self.upload_audio, **btn_style)
        btn_UploadAudio.place(x=157, y=166, height=30, width=113)
        btn_UploadAudio.configure(**btnActive_style)

    def select_path(self):
        self.diretorio_url.set(filedialog.askdirectory())

    def validacao(self, type_extension):
        strUrls = str(self.video_url.get()).strip()
        strPath = str(self.diretorio_url.get()).strip().replace("/", "\\")

        if strUrls == '' or strPath == '':
            messagebox.showinfo('Campo não preenchido!', 'Preencha os campos.')
        elif not os.path.exists(strPath):
            messagebox.showinfo('Diretório não existe!', 'Diretório informado não existe.')
        else:
            urls = strUrls.split(' ')

            progress_bar = ttk.Progressbar(self, variable=self.progressNum, maximum=100, mode='determinate')
            progress_bar.place(x=28, y=285, width=444)
            lbl_title = tk.Label(self, textvariable=self.titleVideoBaixando, font='Arial 10 bold', foreground='white', bg='#2B2B2B')
            lbl_title.place(x=28, y=260)

            success = True

            for index, url in enumerate(urls):
                try:
                    video = YouTube(url, on_progress_callback=self.progress_callback)
                    title_file = re.sub(r'[\\/:*?"<>|]', '_', video.title)[0:90]
                    self.titleVideoBaixando.set(str(index) + '/' + str(len(urls)) + " - '" + title_file + "'")
                    self.progressNum.set(0)
                    self.update()

                    if type_extension == 'mp4':
                        stream = video.streams.get_highest_resolution()

                        if stream:
                            stream.download(output_path=strPath, filename=f'{title_file}.mp4')
                        else:
                            messagebox.showinfo('Formato Invalido!', 'Não é um vídeo mp4:' + url)
                    elif type_extension == 'mp3':
                        audio_stream = video.streams.filter(only_audio=True).first()

                        if audio_stream:
                            audio_stream.download(output_path=strPath, filename=f'{title_file}.mp3')
                        else:
                            messagebox.showinfo('Formato Inválido!', 'Não é possível encontrar uma stream de áudio para:' + url)
                except Exception as e:
                    messagebox.showwarning('Erro!', f'Erro: {e}')
                    success = False

            progress_bar.destroy()
            lbl_title.destroy()
            self.update()

            if success:
                messagebox.showinfo('Sucesso!', 'Baixado com Sucesso')



    def upload_video(self):
        self.validacao('mp4')

    def upload_audio(self):
        self.validacao('mp3')

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        self.progressNum.set(int((bytes_downloaded / total_size) * 100))
        self.update()


if __name__ == "__main__":
    app = Template()
    app.mainloop()
