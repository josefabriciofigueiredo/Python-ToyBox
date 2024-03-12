import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import bd

import webbrowser

# Var globais
ativo_chatBot = [False, None]
chatbot_bd_conexao = bd.ChatBot_BD('ChatBot.db')


class Template(tk.Tk):
    global ativo_chatBot

    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(PagePrincipal)

        # Configurações do Painel
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title("ChatBot RH")
        self.iconbitmap('img/icon.ico')
        w = int(self.winfo_screenwidth() / 2 - 350)
        h = int(self.winfo_screenheight() / 2 - 250)
        self.geometry(f'700x500+{w}+{h}')
        self.resizable(False, False)

        # Barra de Menu
        menu = tk.Menu(self)
        menu.add_command(label="Configuração", command=lambda: self.switch_frame(PagePrincipal))
        menu.add_command(label='Candidatos', command=lambda: self.switch_frame(PageOne))
        self.config(menu=menu)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.place(x=0, y=0, width=700, height=500)

    def close(self):
        if ativo_chatBot[0]:
            ativo_chatBot[1].terminate()
        exit(0)


class PagePrincipal(tk.Frame):
    global ativo_chatBot
    global chatbot_bd_conexao

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.ativado_telaAdicionar = False

        # Configurações do Painel
        self.config(bg="white")

        # Estilos
        lbl_style = {'font': 'Arial 12 bold', 'bg': 'white', 'foreground': '#4E4E4E'}
        btn_style = {'font': 'Arial 10 bold', 'bg': '#D60000', 'foreground': 'white', 'bd': 0}
        btnActive_style = {'activebackground': '#E52828', 'activeforeground': 'white'}

        # Componentes
        tk.Label(self, text="Mensagem Introdutória", **lbl_style).place(x=20, y=20, height=20)

        self.msg_introdutoria = tk.Text(self, bd=1, relief="solid", font=("Arial", 11))
        self.msg_introdutoria.place(x=20, y=50, height=80, width=660)
        self.msg_introdutoria.configure(padx=5, pady=5)

        tk.Label(self, text="Perguntas Frequêntes", **lbl_style).place(x=20, y=170, height=20)

        self.imgAdd = tk.PhotoImage(file='./img/add.png')
        btn_Adicionar = tk.Button(self, image=self.imgAdd, bg='white', bd=0, command=self.telaAdicionar)
        btn_Adicionar.place(x=660, y=170, height=26, width=26)
        btn_Adicionar.configure(activebackground='white')

        self.imgDeletar = tk.PhotoImage(file='./img/delete.png')
        btn_Deletar = tk.Button(self, image=self.imgDeletar, bg='white', bd=0, command=self.deletarPerguntaResposta)
        btn_Deletar.place(x=630, y=170, height=26, width=26)
        btn_Deletar.configure(activebackground='white')

        self.tbl_perguntasRespostas = ttk.Treeview(self, columns=('0', '1', '2'), show='headings')
        self.tbl_perguntasRespostas.column("0", minwidth=20, width=100)
        self.tbl_perguntasRespostas.column("1", minwidth=20, width=100)
        self.tbl_perguntasRespostas.column("2", minwidth=20, width=100)
        self.tbl_perguntasRespostas.heading("0", text="ID")
        self.tbl_perguntasRespostas.heading("1", text="Perguntas")
        self.tbl_perguntasRespostas.heading("2", text="Respostas")
        self.tbl_perguntasRespostas.place(x=20, y=200, height=200, width=660)

        if not chatbot_bd_conexao.sqlCommit('SELECT * FROM perguntas_respostas LIMIT 1').fetchone():
            chatbot_bd_conexao.sqlCommit('INSERT INTO perguntas_respostas (id, pergunta, resposta) VALUES (?, ?, ?)', (1, 'msg', self.msg_introdutoria.get("1.0", "end-1c")))

        for index, valor in enumerate(chatbot_bd_conexao.sqlCommit('SELECT * FROM perguntas_respostas').fetchall()):
            if index != 0:
                self.tbl_perguntasRespostas.insert('', 'end', values=(valor[0], valor[1], valor[2]))
            else:
                self.msg_introdutoria.insert(tk.END, valor[2])

        btn_SalvarInformacoes = tk.Button(self, text='SALVAR', **btn_style, command=self.salvarInformacoes)
        btn_SalvarInformacoes.place(x=20, y=430, height=30, width=100)
        btn_SalvarInformacoes.configure(**btnActive_style)

        self.btn_AtivarChatbot = tk.Button(self, text=("DESATIVAR CHATBOT" if ativo_chatBot[0] else "ATIVAR CHATBOT"), **btn_style, command=self.ativarChatBot)
        self.btn_AtivarChatbot.place(x=130, y=430, height=30, width=160)
        self.btn_AtivarChatbot.configure(**btnActive_style)

    def salvarInformacoes(self):
        if self.msg_introdutoria.get("1.0", "end-1c") != "":
            chatbot_bd_conexao.sqlCommit('UPDATE perguntas_respostas SET resposta = ? WHERE id = ?', (self.msg_introdutoria.get("1.0", "end-1c"), 1))

    def deletarPerguntaResposta(self):
        if len(self.tbl_perguntasRespostas.selection()) == 1:
            resposta = messagebox.askyesno("Confirmação", "Deseja realmente deletar?")
            if resposta:
                chatbot_bd_conexao.sqlCommit('DELETE FROM perguntas_respostas WHERE id = ?', (self.tbl_perguntasRespostas.item(self.tbl_perguntasRespostas.selection()[0], "values")[0],))
                self.tbl_perguntasRespostas.delete(self.tbl_perguntasRespostas.selection()[0])
        else:
            messagebox.showinfo("Informação", "Selecione uma pergunta na tabela para deletar.")

    def telaAdicionar(self):
        if not self.ativado_telaAdicionar:
            self.ativado_telaAdicionar = True
            TelaAdicionar(self)

    def ativarChatBot(self):
        global ativo_chatBot

        if not ativo_chatBot[0]:
            self.btn_AtivarChatbot.config(text="DESATIVAR CHATBOT")
            ativo_chatBot[0] = True
            ativo_chatBot[1] = subprocess.Popen(["python", "bot.py"])
        else:
            self.btn_AtivarChatbot.config(text="ATIVAR CHATBOT")
            ativo_chatBot[0] = False
            ativo_chatBot[1].terminate()


class PageOne(tk.Frame):
    global chatbot_bd_conexao

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Configurações do Painel
        self.config(bg="white")

        # Estilos
        lbl_style = {'font': 'Arial 12 bold', 'bg': 'white', 'foreground': '#4E4E4E'}
        btn_style = {'font': 'Arial 10 bold', 'bg': '#D60000', 'foreground': 'white', 'bd': 0}
        btnActive_style = {'activebackground': '#E52828', 'activeforeground': 'white'}

        # Componentes
        tk.Label(self, text="Lista dos Candidatos", **lbl_style).place(x=20, y=20, height=20)

        self.imgRefresh = tk.PhotoImage(file='./img/refresh.png')
        btn_atualizarTabela = tk.Button(self, image=self.imgRefresh, bg='white', bd=0, command=self.atualizarTabela)
        btn_atualizarTabela.place(x=650, y=20, height=26, width=26)
        btn_atualizarTabela.configure(activebackground='white')

        self.tbl_perguntasRespostas = ttk.Treeview(self, columns=('0', '1', '2', '3'), show='headings')
        self.tbl_perguntasRespostas.column("0", minwidth=20, width=100)
        self.tbl_perguntasRespostas.column("1", minwidth=20, width=100)
        self.tbl_perguntasRespostas.column("2", minwidth=20, width=100)
        self.tbl_perguntasRespostas.column("3", minwidth=20, width=100)
        self.tbl_perguntasRespostas.heading("0", text="Nome")
        self.tbl_perguntasRespostas.heading("1", text="Tel.")
        self.tbl_perguntasRespostas.heading("2", text="E-mail")
        self.tbl_perguntasRespostas.heading("3", text="Local")
        self.tbl_perguntasRespostas.place(x=20, y=50, height=350, width=660)

        self.atualizarTabela()

        btn_AbrirCurriculo = tk.Button(self, text='ABRIR CURRÍCULO', **btn_style, command=self.abrirCurriculo)
        btn_AbrirCurriculo.place(x=20, y=430, height=30, width=160)
        btn_AbrirCurriculo.configure(**btnActive_style)

    def atualizarTabela(self):
        itens = self.tbl_perguntasRespostas.get_children()
        for item in itens:
            self.tbl_perguntasRespostas.delete(item)

        for index, valor in enumerate(chatbot_bd_conexao.sqlCommit('SELECT * FROM candidatos').fetchall()):
            self.tbl_perguntasRespostas.insert('', 'end', values=(valor[0], valor[1], valor[2], valor[3]))

    def abrirCurriculo(self):
        if len(self.tbl_perguntasRespostas.selection()) == 1:
            webbrowser.open(os.getcwd() + "/curriculos/" + self.tbl_perguntasRespostas.item(self.tbl_perguntasRespostas.selection()[0], "values")[0] + ".pdf")
        else:
            messagebox.showinfo("Informação", "Selecione um indivíduo na tabela para acessar o currículo.")


class TelaAdicionar(tk.Tk):
    global chatbot_bd_conexao

    def __init__(self, master):
        super().__init__()
        self.master = master

        # Configurações do Painel
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.config(bg="white")
        self.title("ChatBot RH")
        self.iconbitmap('img/icon.ico')
        w = int(self.winfo_screenwidth() / 2 - 180)
        h = int(self.winfo_screenheight() / 2 - 115)
        self.geometry(f'340x230+{w}+{h}')
        self.resizable(False, False)
        self.title("Adicionar")

        # Estilos
        lbl_style_title = {'font': 'Arial 12 bold', 'bg': 'white', 'foreground': '#4E4E4E'}
        btn_style = {'font': 'Arial 10 bold', 'bg': '#4294FF', 'foreground': 'white', 'bd': 0}
        btnActive_style = {'activebackground': '#6FADFF', 'activeforeground': 'white'}

        # Componentes
        tk.Label(self, text="Pergunta", **lbl_style_title).place(x=20, y=20, height=20)

        self.entry_pergunta = tk.Entry(self, font='Arial 10', bg='white', highlightthickness=0.5, insertbackground='black')
        self.entry_pergunta.place(x=20, y=50, height=30, width=280)

        tk.Label(self, text="Resposta", **lbl_style_title).place(x=20, y=100, height=20)

        self.entry_resposta = tk.Entry(self, font='Arial 10', bg='white', highlightthickness=0.5, insertbackground='black')
        self.entry_resposta.place(x=20, y=130, height=30, width=280)

        btn_Add = tk.Button(self, text='ADICIONAR', **btn_style, command=self.inserirItemTabela)
        btn_Add.place(x=20, y=180, height=30, width=150)
        btn_Add.configure(**btnActive_style)

    def inserirItemTabela(self):
        pergunta = self.entry_pergunta.get()
        resposta = self.entry_resposta.get()
        self.master.ativado_telaAdicionar = False

        id_inserido = chatbot_bd_conexao.sqlCommit('INSERT INTO perguntas_respostas (pergunta, resposta) VALUES (?, ?)', (pergunta, resposta)).lastrowid
        self.master.tbl_perguntasRespostas.insert('', 'end', values=(id_inserido, pergunta, resposta))

        self.destroy()

    def close(self):
        self.master.ativado_telaAdicionar = False
        self.destroy()


if __name__ == "__main__":
    app = Template()
    app.mainloop()
