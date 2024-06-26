import random
import curses
from curses import textpad
import argparse

class BingoCard:
    #Konstruktor BingoCard, Originalkarte wird als Kopie gespeichert.
    def __init__(self, rows, cols, words):
        self.rows = rows
        self.cols = cols
        #Attribut Karte wird mit Methode create_card erstellt
        self.card = self.create_card(words)
        self.original_card = [row[:] for row in self.card]  # Kopie der Originalkarte, um später die Klicks auch rückgängig machen zu können

    #gibt liste mit wörtern aus wordfile wieder
    def create_card(self, words):
        #leere Liste
        card = []
        used_words = set()  # Verwendete Wörter speichern, um Duplikate zu vermeiden, jedes Element im Set kann nur einmal vorkommen

        # Zufällige Wörter in die Karte einfügen
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                #von der Logik durchgehen
                if self.rows % 2 != 0 and self.cols % 2 != 0 and i == self.rows // 2 and j == self.cols // 2:
                    row.append('X')  # Mittleres Feld als Joker, Symbol 'X' verwendet
                else:
                    word = random.choice(words)
                    while word in used_words:
                        word = random.choice(words)
                    row.append(self.split_word(word))
                    used_words.add(word)
            card.append(row)
        return card

    def split_word(self, word):
        # Keine Zeilentrennung, das Wort bleibt in einer Zeile
        return word

    def check_bingo(self):
        # Horizontale Überprüfung
        for row in self.card:
            if all(cell == 'X' for cell in row):
                return True

        # Vertikale Überprüfung
        for col in range(self.cols):
            if all(self.card[row][col] == 'X' for row in range(self.rows)):
                return True

        # Diagonale Überprüfung (von links oben nach rechts unten)
        if all(self.card[i][i] == 'X' for i in range(min(self.rows, self.cols))):
            return True

        # Diagonale Überprüfung (von rechts oben nach links unten)
        if all(self.card[i][self.cols - i - 1] == 'X' for i in range(min(self.rows, self.cols))):
            return True

        return False

    def mark(self, row, col):
        self.card[row][col] = 'X'  # Markieren mit einem Kreuz

    def unmark(self, row, col):
        if self.card[row][col] == 'X':  # Nur wenn es sich nicht um das Jokerfeld handelt
            self.card[row][col] = self.original_card[row][col]  # Rücksetzen auf das Originalwort

    def __str__(self):
        card_str = ""
        for row in self.card:
            # Für jede Zeile in der BingoCard wird eine Zeichenkette erstellt. Zellen der Zeile sind durch "|" getrennt.
            card_str += " | ".join(f"{cell:15}" for cell in row) + "\n"
        # Rückgabe sind alle Wörter als String. Jedes Wort ist eine Zelle, 15 Zeichen breit, und Zellen werden mit "|" getrennt
        return card_str

def draw_card(stdscr, card, marked, field_width, field_height, color_pair):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()  # Maximale Größe des Fensters
    for i, row in enumerate(card):
        for j, word in enumerate(row):
            x1, y1 = 2 + j * (field_width + 1), 2 + i * (field_height + 1)
            x2, y2 = x1 + field_width, y1 + field_height
            # Überprüfen, ob die Koordinaten innerhalb der Fenstergrenzen liegen
            if y2 >= max_y or x2 >= max_x:
                continue
            textpad.rectangle(stdscr, y1, x1, y2, x2)   # Zeichnet eine Umrandung um jedes Feld
            if (i, j) in marked:
                stdscr.addstr(y1 + (field_height // 2), x1 + 1, "X".center(field_width - 1),curses.A_REVERSE | color_pair) # Wenn markiert, dann 'X'
            else:
                stdscr.addstr(y1 + (field_height // 2), x1 + 1, word.center(field_width - 1), color_pair)
        stdscr.addstr(max_y - 2, 2, "Drücke 'x', um das Spiel zu beenden", curses.A_BOLD | color_pair) # Programm wird abgebrochen, wenn x gedrückt wird.
        stdscr.refresh()

def main(stdscr, xaxis, yaxis, words):
    curses.start_color()
    # Farbpaar als Attribut in Curses für färben der Wörter
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    color_pair = curses.color_pair(1)
    yellow_blue = curses.color_pair(2)

    #Erstellen einer Bingo-Instanz
    bingo_card = BingoCard(xaxis, yaxis, words)
    card = bingo_card.card
    marked = set()

    # Automatisches Markieren des mittleren Feldes, wenn xaxis und yaxis gleich und ungerade sind
    if xaxis == yaxis and xaxis % 2 == 1:
        middle = xaxis // 2
        marked.add((middle, middle))

    # Berechnen der Feldgröße basierend auf der Länge des längsten Wortes
    #To-Do: umschreiben auf Wörter, die in der BingoCard sind -> noch dynamischer
    longest_word_length = max(len(word) for word in words)
    field_width = longest_word_length + 2 # Zusätzlicher Platz für das Wort und die Ränder
    field_height = 4  # Feste Höhe des Feldes

    # Folgende Zeilen stellen sicher, dass Mausereignisse von curses erkannt werden:
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    draw_card(stdscr, card, marked, field_width, field_height, color_pair)

    while True:
        key = stdscr.getch()
        if key == ord('x'):
            break
        # Klick ist ein Mausereignis
        if key == curses.KEY_MOUSE:  # Überprüft, ob das Ereignis key ein Mausereignis ist
            _, mx, my, _, _ = curses.getmouse()  # Mausposition wird abgerufen
            col = (mx - 2) // (field_width + 1)
            row = (my - 2) // (field_height + 1)
            if 0 <= row < xaxis and 0 <= col < yaxis:
                if (row, col) in marked:
                    marked.remove((row, col))
                    bingo_card.unmark(row, col)
                else:
                    marked.add((row, col))
                    bingo_card.mark(row, col)
                draw_card(stdscr, card, marked, field_width, field_height, color_pair)
                if bingo_card.check_bingo():
                    stdscr.addstr(2 + xaxis * (field_height + 1), 2, "BINGO! Du hast gewonnen!".center((field_width + 1) * yaxis), yellow_blue)
                    stdscr.refresh()
                    while True:
                        key = stdscr.getkey()
                        if key == "x":
                            break
                    break

# Datei wird im Lesemodus geöffnet und jede Zeile ist ein Index im Array
def load_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Fehler: Datei '{file_path}' nicht gefunden.")
        while True:
            user_choice = input("Möchten Sie die Standardwörter verwenden (Option 1) oder einen anderen Dateipfad angeben (Option 2)?")

            if user_choice == '1':
                print("Standardwörter werden verwendet.")
                default_words = [
                    "Synergie", "Rating", "Wertschöpfend", "Benefits", "Ergebnisorientiert", "Nachhaltig",
                    "Hut aufhaben",
                    "Visionen", "Zielführend", "Global Player", "Rund sein", "Szenario", "Diversity",
                    "Corporate Identitiy",
                    "Fokussieren", "Impact", "Target", "Benchmark", "Herausforderung(en)/Challenges", "Gadget", "Value",
                    "Smart",
                    "Web 2.0 oder 3.0", "Qualität", "Big Picture", "Revolution", "Pro-aktiv", "Game-changing", "Blog",
                    "Community",
                    "Social Media", "SOA", "Skalierbar", "Return on Invest (ROI)", "Wissenstransfer", "Best Practice",
                    "Positionierung/Positionieren", "Committen", "Geforwarded", "Transparent", "Open Innovation",
                    "Out-of-the-box",
                    "Dissemination", "Blockchain", "Skills", "Gap", "Follower", "Win-Win", "Kernkomp"
                ]
                return random.sample(default_words, len(default_words))
            elif user_choice == '2':
                file_path = input("Bitte geben Sie den Dateipfad zur Wortdatei ein: ")
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return [line.strip() for line in file]
                except FileNotFoundError:
                    print(f"Fehler: Datei '{file_path}' nicht gefunden. Bitte versuchen Sie es erneut.")
            else:
                print("Ungültige Eingabe. Bitte wählen Sie entweder Option 1 oder Option 2.")

# Argumentparsing und anschließendes Aufrufen des curses.wrapper
#wird immer als erstes ausgeführt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bingo-Spiel")
    parser.add_argument('-xaxis', type=int, default=5, help='Anzahl der Felder in der Breite')
    parser.add_argument('-yaxis', type=int, default=5, help='Anzahl der Felder in der Höhe')
    parser.add_argument('-wordfile', type=str, default='wordfile.txt', help='Pfad zur Datei mit den Wörtern')
    args = parser.parse_args()

    try:
        #wörter aus angegebener Datei werden geladen
        words = load_words(wordfile)
        if len(words) < xaxis * yaxis:
            raise ValueError("Nicht genügend Wörter in der Datei, um die Bingo-Karte zu füllen.")

        #Die Main-Methode wird als Curses Umgebung gestartet
        curses.wrapper(main, xaxis, yaxis, words)
    except FileNotFoundError as e:
        print(e)
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)