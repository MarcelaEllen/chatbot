import customtkinter as ctk
import requests
import csv
from io import StringIO

class NutriBot:
    def __init__(self, master):
        self.master = master
        master.title("NutriBot")
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
        self.text_area.insert(ctk.END, "Olá! Eu sou o NutriBot. Como posso te ajudar com suas dúvidas nutricionais?\n")
        self.text_area.configure(state="disabled")  # Apenas leitura na área de texto

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite o nome do alimento...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="green", command=self.process_input)
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
        self.text_area.insert(ctk.END, "NutriBot: " + response + "\n")
        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

    def get_response(self, user_input):
        # URL para o CSV exportado da planilha pública do Google Sheets
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQQnLPXBywPKV-99eANe7PzzVMuNBjzX_QWsMG-br21wC2VkwCl67pl6-xbfwgza0A0FK3hkCiqJeki/pub?output=csv"

        try:
            # Fazer a requisição para a URL do Google Sheets em formato CSV
            response = requests.get(sheet_url)
            if response.status_code == 200:
                csv_data = response.text

                # Processar o conteúdo CSV
                csv_reader = csv.reader(StringIO(csv_data))
                next(csv_reader)  # Pular o cabeçalho da tabela

                # Procurar o alimento na tabela
                for row in csv_reader:
                    nome = row[0].strip().lower()
                    if nome == user_input.lower():
                        calorias = row[1]
                        proteinas = row[2]
                        carboidratos = row[3]
                        gorduras = row[4]
                        return (f"{nome.capitalize()}:\n"
                                f"Calorias: {calorias} kcal\n"
                                f"Proteínas: {proteinas} g\n"
                                f"Carboidratos: {carboidratos} g\n"
                                f"Gorduras: {gorduras} g")
                return "Desculpe, não encontrei informações sobre esse alimento. Tente outro."
            else:
                return "Desculpe, não consegui acessar a tabela no momento."
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar com a tabela: {e}"

if __name__ == "__main__":
    root = ctk.CTk()
    nutri_bot = NutriBot(root)
    root.mainloop()
