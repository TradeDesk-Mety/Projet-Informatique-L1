import os
import re

# Nettoyage et injection globale dans les pages
pages_dir = "/home/tim/Desktop/Projet-Informatique-L1/website/pages"
for file in os.listdir(pages_dir):
    if file.endswith(".py"):
        path = os.path.join(pages_dir, file)
        with open(path, "r") as f:
            content = f.read()
            
        # Ajout de ui_config
        if "set_global_ui" not in content:
            content = content.replace("from website.components.assistant_sidebar import render_assistant", "from website.components.assistant_sidebar import render_assistant\nfrom website.components.ui_config import set_global_ui")
            content = content.replace("render_assistant()", "set_global_ui()\nrender_assistant()")
            
        with open(path, "w") as f:
            f.write(content)

# Nettoyage de TradeDesk.py (anciennement web.py)
main_file = "/home/tim/Desktop/Projet-Informatique-L1/website/TradeDesk.py"
with open(main_file, "r") as f:
    content = f.read()

# Remplacement de email par nom d'utilisateur
content = content.replace("Adresse e-mail", "Nom d'utilisateur")
content = content.replace("vous@example.com", "Votre pseudo")
content = content.replace("Cette adresse e-mail", "Ce nom d'utilisateur")
content = content.replace("email =", "username =")

# Suppression de l'ancien CSS
content = re.sub(r"st\.markdown\(\"\"\"\s*<style>.*?</style>\s*\"\"\", unsafe_allow_html=True\)", "", content, flags=re.DOTALL)

# Ajout de ui_config
if "set_global_ui" not in content:
    content = content.replace("from equities.equities import Portfolio", "from equities.equities import Portfolio\nfrom website.components.ui_config import set_global_ui\nfrom website.components.assistant_sidebar import render_assistant")
    content = re.sub(r"(st\.set_page_config\(.*?\))", r"\1\nset_global_ui()", content, flags=re.DOTALL)
    
with open(main_file, "w") as f:
    f.write(content)
