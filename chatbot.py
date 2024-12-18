import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import spacy
from difflib import SequenceMatcher

nlp = spacy.load('pt_core_news_sm')

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Artemis")
        master.geometry("600x500")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("dark-blue")  # Temas disponíveis: "blue", "green", "dark-blue"

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Artemis, sua nutri virtual. Me diga um alimento para que eu te informe a sua composição!\n")
        self.text_area.configure(state="disabled")  # Apenas leitura na área de texto

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite o nome do alimento...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        # Processar a entrada do usuário
        response = self.get_response(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")
        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

    def get_response(self, user_input):
        # Consultar a tabela
        try:
            response = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vQQnLPXBywPKV-99eANe7PzzVMuNBjzX_QWsMG-br21wC2VkwCl67pl6-xbfwgza0A0FK3hkCiqJeki/pubhtml?gid=0&single=true")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')

                # Criar uma lista de alimentos e seus dados
                alimentos = {}
                for row in rows[1:]:  # Pular o cabeçalho
                    cells = row.find_all('td')
                    alimento = cells[0].get_text().strip()
                    calorias = cells[1].get_text().strip()
                    proteinas = cells[2].get_text().strip()
                    carboidratos = cells[3].get_text().strip()
                    gorduras = cells[4].get_text().strip()
                    alimentos[alimento.lower()] = (calorias, proteinas, carboidratos, gorduras)

                # Processar o input com spaCy
                doc = nlp(user_input.lower())
                tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]

                # Verificar correspondência exata
                for token in tokens:
                    if token in alimentos:
                        calorias, proteinas, carboidratos, gorduras = alimentos[token]
                        return (f"Alimento: {token.capitalize()}\n"
                                f"Calorias: {calorias} kcal\n"
                                f"Proteínas: {proteinas} g\n"
                                f"Carboidratos: {carboidratos} g\n"
                                f"Gorduras: {gorduras} g")

                # Buscar correspondência por similaridade
                melhor_correspondencia = None
                maior_similaridade = 0
                for alimento in alimentos.keys():
                    for token in tokens:
                        similaridade = SequenceMatcher(None, token, alimento).ratio()
                        if similaridade > maior_similaridade:
                            maior_similaridade = similaridade
                            melhor_correspondencia = alimento

                if maior_similaridade > 0.8:  # Limite de similaridade para sugestões
                    calorias, proteinas, carboidratos, gorduras = alimentos[melhor_correspondencia]
                    return (f"Você quis dizer '{melhor_correspondencia.capitalize()}'?\n"
                            f"Calorias: {calorias} kcal\n"
                            f"Proteínas: {proteinas} g\n"
                            f"Carboidratos: {carboidratos} g\n"
                            f"Gorduras: {gorduras} g")

                return "Alimento não encontrado. Por favor, verifique o nome e tente novamente."
            else:
                return "Desculpe, não consegui acessar a tabela no momento."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
