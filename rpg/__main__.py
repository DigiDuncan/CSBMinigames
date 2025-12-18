import rpg.content as content

from rpg.console import Fight

if __name__ == "__main__":
    Fight((content.Characters.CS, content.Characters.CS, content.Characters.CS,), (content.Characters.COP, content.Characters.COP, content.Characters.COP,), show_debug=False).run()