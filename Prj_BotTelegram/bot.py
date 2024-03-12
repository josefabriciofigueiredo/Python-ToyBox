import telebot
import bd


def main(token):
    bot = telebot.TeleBot(token)

    msg_introdutoria = ""
    msg_nao_identificado = "Não identificamos o seu interesse. Escolha o que você precissa:\n/Inscrever\n/Sobre\n/MinhasInformacoes"
    list_perguntas = {}
    sessao = {}

    chatbot_bd_conexao = bd.ChatBot_BD('ChatBot.db')
    for index, valor in enumerate(chatbot_bd_conexao.sqlCommit('SELECT * FROM perguntas_respostas').fetchall()):
        if index != 0:
            list_perguntas[str(index - 1)] = [valor[1], valor[2]]
        else:
            msg_introdutoria = valor[2]

    @bot.message_handler(commands=list(list_perguntas.keys()))
    def respostasVaga(msg):
        if sessao.get(msg.chat.id) == "Sobre":
            bot.send_message(msg.chat.id, list_perguntas[msg.text[1:]][1])
        else:
            bot.send_message(msg.chat.id, msg_nao_identificado)
            sessao[msg.chat.id] = ""

    @bot.message_handler(commands=["Sobre"])
    def perguntasVaga(msg):
        sessao[msg.chat.id] = "Sobre"
        mensagem = "Perguntas sobre a vaga:"
        for key in list_perguntas.keys():
            mensagem += "\n /" + key + " - " + list_perguntas[key][0]
        bot.send_message(msg.chat.id, mensagem)

    @bot.message_handler(commands=["Inscrever"])
    def inscrever(msg):
        chatbot_bd_conexao = bd.ChatBot_BD('ChatBot.db')

        if not chatbot_bd_conexao.sqlCommit('SELECT * FROM candidatos WHERE id = ?', (msg.chat.id,)).fetchone():
            chatbot_bd_conexao.sqlCommit('INSERT INTO candidatos (id) VALUES (?)', (msg.chat.id,))

            bot.send_message(msg.chat.id, "Solicitaremos algumas informações...\nInforme o seu nome:")
            sessao[msg.chat.id] = "Inscrever-Nome"
        else:
            bot.send_message(msg.chat.id, "Temos algumas informações no nosos banco de dados, deseja edita-las?\n/Sim\n/Nao")
            sessao[msg.chat.id] = "Editar"

    @bot.message_handler(commands=["MinhasInformacoes"])
    def minhasInformacoes(msg):
        chatbot_bd_conexao = bd.ChatBot_BD('ChatBot.db')
        res = chatbot_bd_conexao.sqlCommit('SELECT * FROM candidatos WHERE id = ?', (msg.chat.id,)).fetchall()

        if len(res) != 0:
            sessao[msg.chat.id] = "Editar"

            mensagem = "Suas informações: "
            mensagem += "\n\nNome: " + res[0][1]
            mensagem += "\nTel.: " + res[0][4]
            mensagem += "\nEndereço: " + res[0][3]
            mensagem += "\nE-mail: " + res[0][2]
            mensagem += "\nReenviar um novo Currículo"
            mensagem += "\n\nDeseja editar alguma infomação? /Sim /Nao"
        else:
            mensagem = "Você precisa se /Inscrever"

        bot.send_message(msg.chat.id, mensagem)

    @bot.message_handler(commands=["Sim", "Nao"])
    def opcaoSimNao(msg):
        if sessao.get(msg.chat.id) == "Editar":
            if msg.text[1:] == "Sim":
                bot.send_message(msg.chat.id, "O que precisa editar?\n/Nome\n/Tel\n/Endereco\n/Email\n/Curriculo")
            else:
                sessao[msg.chat.id] = ""
        else:
            sessao[msg.chat.id] = ""
            bot.send_message(msg.chat.id, msg_nao_identificado)

    @bot.message_handler(commands=["Nome", "Tel", "Endereco", "Email", "Curriculo"])
    def atualizarDados(msg):
        mensagem = ""
        if sessao.get(msg.chat.id) == "Editar":
            match msg.text[1:]:
                case "Nome":
                    mensagem = "Informe o seu nome: "
                    sessao[msg.chat.id] = "Editar-Nome"
                case "Endereco":
                    mensagem = "Informe o seu endereço: "
                    sessao[msg.chat.id] = "Editar-Endereco"
                case "Email":
                    mensagem = "Informe o seu e-mail: "
                    sessao[msg.chat.id] = "Editar-Email"
                case "Tel":
                    mensagem = "Informe o seu telefone: "
                    sessao[msg.chat.id] = "Editar-Tel"
                case "Curriculo":
                    mensagem = "Compartilhe o seu currículo em PDF: "
                    sessao[msg.chat.id] = "Editar-Curriculo"
        else:
            mensagem = msg_nao_identificado
            sessao[msg.chat.id] = ""

        bot.send_message(msg.chat.id, mensagem)

    @bot.message_handler(content_types=['document'])
    def download_documento(msg):
        if msg.document.mime_type == 'application/pdf':
            file_info = bot.get_file(msg.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open('curriculos/' + str(msg.chat.id) + '.pdf', 'wb') as new_file:
                new_file.write(downloaded_file)

            if sessao.get(msg.chat.id) == "Editar-Curriculo":
                bot.send_message(msg.chat.id, "Currículo compartilhado com sucesso")
                sessao[msg.chat.id] = ""
            elif sessao.get(msg.chat.id) == "Inscrever-Curriculo":
                bot.send_message(msg.chat.id,"Cadastrado com sucesso na vaga. Espere as orientações do RH.\nCaso necessite é permitido editar suas informações /MinhasInformacoes")
                sessao[msg.chat.id] = ""
        else:
            bot.send_message(msg.chat.id, "O arquivo enviado não é um PDF. Envie outro novamente:")

    @bot.message_handler()
    def start(msg):
        chatbot_bd_conexao = bd.ChatBot_BD('ChatBot.db')

        match sessao.get(msg.chat.id):
            case "Inscrever-Nome":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET nome = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Informe o seu telefone:")
                sessao[msg.chat.id] = "Inscrever-Tel"
            case "Inscrever-Tel":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET telefone = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Informe o seu Endereço:")
                sessao[msg.chat.id] = "Inscrever-Endereco"
            case "Inscrever-Endereco":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET endereco = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Informe o seu E-mail:")
                sessao[msg.chat.id] = "Inscrever-Email"
            case "Inscrever-Email":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET email = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Compartilhe o seu currículo em PDF: ")
                sessao[msg.chat.id] = "Inscrever-Curriculo"
            case "Editar-Nome":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET nome = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Nome atualizado com sucesso")
                sessao[msg.chat.id] = ""
            case "Editar-Tel":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET telefone = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Telefone atualizado com sucesso")
                sessao[msg.chat.id] = ""
            case "Editar-Endereco":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET endereco = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "Endereço atualizado com sucesso")
                sessao[msg.chat.id] = ""
            case "Editar-Email":
                chatbot_bd_conexao.sqlCommit('UPDATE candidatos SET email = ? WHERE id = ?', (msg.text, msg.chat.id))

                bot.send_message(msg.chat.id, "E-mail atualizado com sucesso")
                sessao[msg.chat.id] = ""
            case _:
                bot.send_message(msg.chat.id, msg_introdutoria)
                sessao[msg.chat.id] = ""

    bot.polling()


if __name__ == "__main__":
    main('Seu_Token')

