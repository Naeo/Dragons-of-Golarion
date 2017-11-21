#!/usr/bin/python3
"""
This program will automatically scrape the In Character Chat channel in 
Riot, parse commands, and generate to a .tex file which can be compiled
with pdfLaTeX or any other modern LaTeX system.  No \usepackage commands
should be needed.

THIRD PARTY LIBRARY REQUIREMENTS (install with pip):
    matrix-client
"""

from copy import deepcopy
from pprint import pprint
import re
from time import sleep

from matrix_client.client import MatrixClient

# replace this text with your Riot API key.
API_KEY = "your api key here"
# replace this with the Riot internal room ID
ROOM_ID = "your room ID here"
# The earliest time chunk in the room--formatted like "t_
SINCE_ID = "oldest timestamp"
# your user id that you log in with, with the leading @
USER_ID = "your user id"
# room's home server--change if not matrix.org
HOME_SERVER = "https://www.matrix.org"

# basic supported commands that can be used in the chats.
COMMANDS = {
    "begin":re.compile("!b(egin)?", re.IGNORECASE),
    "end":re.compile("!e(nd)?", re.IGNORECASE),
    "description":re.compile("!de(sc(r(iption)?)?)?", re.IGNORECASE),
    "do":re.compile("!do", re.IGNORECASE),
    "ignore":re.compile("!i(g(n(ore)?)?)?", re.IGNORECASE),
    "namechange":re.compile("!\[.+?\]", re.IGNORECASE),
}

USER_CHARACTERNAMES = {
    # Add keys here in the form: "riot_ID":"default character name"
    # for everyone in the room.  Use the full riot IDs, e.g.
    # @JohnDoe:matrix.org
}

# deals with bold/italics/underlines in Riot's markdown
FORMAT_DICT = {
    "bold":re.compile(r"\*\*(.*?)\*\*"),
    "italics":re.compile(r"\*(.*?)\*"),
    "underline":re.compile(r"<u>(.*?)</u>"),
}

class Conversation:
    """Class to hold conversation data and generate the .tex file."""
    
    # frontmatter to the .tex file
    latex_start = r"""\documentclass{article}
\usepackage[margin=1in]{geometry}

\newcommand{\DoText}[1]{
\begin{center}
\begin{minipage}{7cm}
\textit{#1}
\end{minipage}
\end{center}
}

\newcommand{\AuthorText}[1]{
\medskip
\parindent=0cm\hangindent=\parindent
\textsc{\Large#1}
\par\parindent=1cm\hangindent=\parindent
}

\newcommand{\SpeechText}[1]{
\begin{flushleft}
\begin{minipage}{9cm}
\parindent=1cm\hangindent=1cm #1
\end{minipage}
\end{flushleft}
}

\begin{document}

\rightskip=0cm\leftskip=0cm

"""

    latex_end = r"""

\end{document}
"""
    
    def __init__(self):
        self.description = ""
        self.events = []
        self.names = deepcopy(USER_CHARACTERNAMES)
        self.tex = self.latex_start
    
    def gen_latex(self):
        # Empty list to store formatted events in as we parse them
        temp_events = []
        
        # start parsing events
        for i in self.events:
            # set defaults
            TYPE = "speech"
            AUTHOR = self.names[i["sender"]]
            
            if COMMANDS["ignore"].match(i["body"]):
                continue
                
            elif COMMANDS["description"].match(i["body"]):
                self.description = i["body"].split(maxsplit=1)[1]
                continue
                
            elif COMMANDS["do"].match(i["body"]):
                TYPE = "do"
                i["body"] = r"\DoText{{{}}}".format(i["body"][3:].strip())
                
            elif COMMANDS["namechange"].match(i["body"]):
                m = COMMANDS["namechange"].match(i["body"])
                # Change author name
                AUTHOR = m.group()[2:-1]
                self.names[i["sender"]] = AUTHOR
                # only namechange, no text                
                if COMMANDS["namechange"].match(i["body"]).group() == i["body"]:
                    continue
                # Remove ![new name] command from body
                i["body"] = r"\SpeechText{{{}}}".format(i["body"][m.span()[1]:])
            
            else:
                # all regular speech events
                i["body"] = r"\SpeechText{{{}}}".format(i["body"])
            
            # Clean up underscore/bold/italics formatting.
            i["body"] = FORMAT_DICT["bold"].sub(
                lambda m: r"\textbf{" + m.groups()[0] + "}",
                i["body"]
            )
            i["body"] = FORMAT_DICT["italics"].sub(
                lambda m: r"\textit{" + m.groups()[0] + "}",
                i["body"]
            )
            i["body"] = FORMAT_DICT["underline"].sub(
                lambda m: r"\underline{" + m.groups()[0] + "}",
                i["body"]
            )
            
            # Append cleaned event to our temporary list
            temp_events.append(
                {
                    "author":AUTHOR,
                    "type":TYPE,
                    "body":i["body"].strip(),
                    "time":i["origin_server_ts"],
                }
            )
                
        self.events = temp_events
        
        # Now, construct the .tex file.
        # Add chat description as a title-like thing
        self.tex += """\\centering\\huge\n{}\n\n\\normalsize\\raggedright""".format(self.description)
        AUTHOR = ""
        TYPE = "speech"
        for i in self.events:
            if i["author"] != AUTHOR and i["type"] != "do":
                self.tex += "\n\n" + r"\AuthorText{{{}}}".format(i["author"])
                AUTHOR = i["author"]

            if i["type"] == "do" and TYPE == "speech":
                self.tex += "\n\n" + r"\medskip " + i["body"]

            elif i["type"] == "speech" and TYPE == "do":
                self.tex += "\n\n" + r"\medskip " + i["body"]

            elif i["type"] == "speech":
                self.tex += "\n\n" + r"\SpeechText{{{}}} ".format(i["body"])

            elif i["type"] == "do":
                self.tex += "\n\n " + i["body"]
            TYPE = i["type"]

        self.tex += self.latex_end
        
        return self.tex
        
    
def pull_room(since=SINCE_ID):
    C = MatrixClient(
        HOME_SERVER,
        token=API_TOKEN,
        user_id=USER_ID
    )

    # the in-character chat room
    room = C.rooms[ROOM_ID]
    room.event_history_limit = -1
    # room.backfill_previous_messages(limit=1000)
    since = room.prev_batch
    while True:
        res = room.client.api.get_room_messages(
            room.room_id,
            since,
            direction="b",
            limit=200,
        )
        # No messages returned --> got all of 'em out of the room
        if len(res["chunk"]) == 0:
            break
        room.events += res["chunk"]
        since = res["end"]
        # Courtesy sleep to not hammer their servers too hard
        sleep(10)
    
    # Filter to only text/message events.  Two rounds of filtering
    # to remove the non-messages first--sometimes errors happen
    # otherwise
    EVENTS = [
        i 
        for i in room.events
        if i["type"] == "m.room.message" 
        and "redacted_because" not in i # removes redacted messages
    ]
    
    EVENTS = [
        i
        for i in EVENTS
        if i["content"]["msgtype"] in {"m.emote", "m.text", "m.message"}
    ]
    # Reshape the entries to extract the body and msgtype keys
    for i in EVENTS:
        i["body"] = i["content"]["body"]
    EVENTS = sorted(EVENTS, key=lambda x:x["origin_server_ts"])
    
    scripts = []
    curscript = Conversation()
    gobble = False
    for i in EVENTS:
        if COMMANDS["begin"].match(i["body"]):
            curscript = Conversation()
            gobble = True
            continue
        elif COMMANDS["end"].match(i["body"]):
            scripts.append(curscript)
            gobble = False
        if gobble is True:
            curscript.events.append(i)
    
    return scripts

df = pull_room()
for i in range(len(df)):
    with open("SCRIPTS/{}.tex".format(i), "w") as F:
        F.write(df[i].gen_latex())
