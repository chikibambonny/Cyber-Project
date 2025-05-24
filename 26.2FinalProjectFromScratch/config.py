# =========== NETWORK ===========

SERVER_HOST: str = "127.0.0.1"
PORT: int = 1113
BUFFER_SIZE: int = 16384
HEADER: str = "04d"
FORMAT: str = 'utf-8'
DISCONNECT_MSG: str = "EXIT"
WELCOME_MSG: str = "Welcome"
MAX_CONNECTIONS: int = 5  # maximal number of players
# COUNT_ANON = 0  # count anonymous players

ACT_DELIMITER = ">"
ARG_DELIMITER = "<"

# =========== ACTIONS ===========
# general
EXIT_ACTION = "EXIT"  # Command for exiting the game
WELCOME_ACTION = "WELCOME"  # Command for welcoming new players
CONNECTION_ACTION = "CONNECTION"
LOGIN_ACTION = "LOGIN"
SIGNUP_ACTION = "SIGNUP"
TEXT_ACTION = "TEXT"  # REGULAR TEXT MESSAGE TO BE BROADCASTED
LOGOUT_ACTION = "LOGOUT"
IMAGE_ACTION = "IMAGE"

# gameplay
DICT_ACTION = "DICTIONARY"
ROLE_ACTION = "ROLE"  # Command for assigning roles
WORD_ACTON = "WORD"  # Command for sending the drawing word
GUESS_ACTION = "GUESS"  # Command for submitting a guess
PLAY_ACTION = "PLAY"  # Command for stopping accepting connections and starting a new game

ACTIONS = [EXIT_ACTION, WELCOME_ACTION, CONNECTION_ACTION, LOGIN_ACTION, SIGNUP_ACTION, TEXT_ACTION, LOGOUT_ACTION,
           IMAGE_ACTION, DICT_ACTION, ROLE_ACTION, WORD_ACTON, GUESS_ACTION, PLAY_ACTION
           ]

# roles
DRAW_ROLE = True
GUESS_ROLE = False

# defaults
ANON_NAME = "Anonymous"

# =========== WORDS ===========
DEFAULT_DICT = "Dictionaries/English.txt"

DICT_DEF = "Default"
DICT_ENGLISH = "English"
DICT_RUSSIAN = "Russian"
DICT_HEBREW = "Hebrew"
DICT_HAMSONGS = "Hamilton"

DICTIONARIES = {
    DICT_DEF: DEFAULT_DICT,
    DICT_ENGLISH: "Dictionaries/English.txt",
    DICT_RUSSIAN: "Dictionaries/Russian.txt",
    DICT_HEBREW: "Dictionaries/Hebrew.txt",
    DICT_HAMSONGS: "Dictionaries/HamiltonSongs.txt"

}


# =========== DATABASE ===========
DATABASE_PATH = "users.db"

# =========== UI ===========
CLIENT_UI = './PYQTDesignerStuff/ClientUI.ui'
CAST_IMG_PATH = "saved_drawings/drawing_20250325_221158.png"

# =========== STYLES ===========
# palette swatches https://coolors.co/f5bd4c-fbf6e3-543e12-ec9146-f4ccc2-7d8458-ffffff-b84169-be5277-c46283
LIGHTBEIGE_BG = "rgb(251, 246, 227)"
BUTTONS = "rgb(245, 189, 76)"
BORDER_BUTTONS = "rgb(236, 145, 70)"
TEXT_BUTTONS = "rgb(251, 246, 227)"
DIS_BUTTONS = "rgb(248, 212, 139)"
DIS_BORDER_BUTTONS = "rgb(243, 189, 144)"  # Fixed typo
FIELDS = "rgb(255, 255, 255)"
LABELS = "rgb(125, 132, 88)"
SHADOW_BUTTONS = "rgb(230, 150, 60)"  # Slightly darker shade for shadow effect
DIS_SHADOW_BUTTONS = "rgb(220, 180, 120)"  # Softer shadow for disabled buttons
TEXT_COL = "rgb(60, 40, 13)"

# drawing window, palette https://coolors.co/c03935-e16a30-f5ad33-387b5c-3877aa-7c6d8e-d691ad-1e0c00-fff4e2
'''
RED = "C03935"
ORANGE = "E16A30"
YELLOW = "F5AD33"
GREEN = "387B5C"
BLUE = "3877AA"
PURPLE = "7C6D8E"
PINK = "D691AD"
BLACK = "2D221E"

'''
RED = "rgb(192, 57, 53)"
ORANGE = "rgb(225, 106, 48)"
YELLOW = "rgb(245, 173, 51)"
GREEN = "rgb(56, 123, 92)"
BLUE = "rgb(56, 119, 170)"
PURPLE = "rgb(124, 109, 142)"
PINK = "rgb(214, 145, 173)"
BLACK = "rgb(30, 12, 0)"
WHITE = "rgb(255, 244, 226)"

PALETTE_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, BLACK]


def set_designs(buttons: list, fields: list, labels: list, dropdowns: list):
    button_style = f"""
    QPushButton:enabled {{ 
        background-color: {BUTTONS};  
        color: {TEXT_BUTTONS};
        border: 2px solid {BORDER_BUTTONS};  /* Main border */
        border-bottom: 4px solid {SHADOW_BUTTONS};  /* Simulated shadow at the bottom */
        border-radius: 8px;
    }}
    QPushButton:disabled {{ 
        background-color: {DIS_BUTTONS};  
        color: {TEXT_BUTTONS};
        border: 2px solid {DIS_BORDER_BUTTONS};  /* Softer border for disabled buttons */
        border-bottom: 4px solid {DIS_SHADOW_BUTTONS};  /* Softer shadow for disabled buttons */
        border-radius: 8px;
    }}
"""
    dropdown_style = f"""
    QComboBox {{
        background-color: {BUTTONS};
        color: {TEXT_BUTTONS};
        border: 2px solid {BORDER_BUTTONS};
        border-bottom: 4px solid {SHADOW_BUTTONS};
        border-radius: 8px;
        qproperty-alignment: 'AlignCenter';
        
    }}
"""

    field_style = f"background-color: {FIELDS}; color: {TEXT_COL}"
    label_style = f"color: {LABELS}"

    for button in buttons:
        button.setStyleSheet(button_style)
    for dropdown in dropdowns:
        dropdown.setStyleSheet(dropdown_style)
    for field in fields:
        field.setStyleSheet(field_style)
    for label in labels:
        label.setStyleSheet(label_style)
