import sqlite3


class ChatBot_BD:
    def __init__(self, name_bd):
        self.conexao = sqlite3.connect(name_bd)

        self.criarTBL_Candidatos()
        self.criarTBL_PerguntasRespostas()

    def criarTBL_Candidatos(self):
        self.conexao.execute('''CREATE TABLE IF NOT EXISTS candidatos (id INTEGER PRIMARY KEY, nome TEXT, email TEXT, endereco TEXT, telefone TEXT)''')
        self.conexao.commit()

    def criarTBL_PerguntasRespostas(self):
        self.conexao.execute('''CREATE TABLE IF NOT EXISTS perguntas_respostas (id INTEGER PRIMARY KEY AUTOINCREMENT, pergunta TEXT, resposta TEXT)''')
        self.conexao.commit()

    def sqlCommit(self, sql, paramentro=()):
        res = self.conexao.cursor().execute(sql, paramentro)
        self.conexao.commit()
        return res

