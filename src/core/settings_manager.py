import json
import os

class SettingsManager:
    def __init__(self):
        # Caminho para salvar as configurações do usuário (na pasta do app ou AppData)
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "user_settings.json")
        self.recents = []
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recents = data.get("recent_projects", [])
            except Exception as e:
                print(f"Erro ao carregar settings: {e}")

    def save_settings(self):
        data = {"recent_projects": self.recents}
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar settings: {e}")

    def add_recent(self, name, path):
        # Remove se já existir para colocar no topo
        self.recents = [r for r in self.recents if r['path'] != path]
        # Adiciona no início
        self.recents.insert(0, {"name": name, "path": path})
        # Mantém apenas os últimos 10
        self.recents = self.recents[:10]
        self.save_settings()

    def get_recents(self):
        return self.recents