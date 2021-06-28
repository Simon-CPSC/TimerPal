#===================================================
# _____ _                     ____       _ 
#|_   _(_)_ __ ___   ___ _ __|  _ \ __ _| |
#  | | | | '_ ` _ \ / _ \ '__| |_) / _` | |
#  | | | | | | | | |  __/ |  |  __/ (_| | |
#  |_| |_|_| |_| |_|\___|_|  |_|   \__,_|_|
#
#   By Simon Robles
#   Credit where credit is due:
#       •https://github.com/trehn/termdown
#===================================================
import time
import os
import curses
import re

from datetime import datetime, timedelta
from math import ceil
from pyfiglet import Figlet
from curses import textpad, ERR
from threading import Thread, Event, Lock
from queue import Queue, Empty
from playsound import playsound

CONVERSION = {"hours": 3600, "minutes": 60, "seconds": 1}
INPUT_EXIT = 1

def inputThreadBody(stdscr, quit_event, curses_lock, input_queue):
    while not quit_event.is_set():
        try:
            with curses_lock:
                key = stdscr.getkey()
        except:
            key = None
        if key in ("q", "Q"):
            input_queue.put(INPUT_EXIT)
        sleep(0.01)

def inputMode(stdscr):
    stdscr.clear()
    screenHeight, screenWidth = stdscr.getmaxyx()
    windowHeight, windowWidth = (1, 30)
    yPos, xPos = (int( 1/2 * (screenHeight - windowHeight)),
                 int(1/2 * (screenWidth - windowWidth)))
    inputWindow = curses.newwin(windowHeight, windowWidth, yPos, xPos)
    textpad.rectangle(stdscr, (yPos - 1), (xPos - 1),
            (yPos + windowHeight), (xPos + windowWidth + 2))
    stdscr.refresh()
    timeTextbox = textpad.Textbox(inputWindow)
    timeTextbox.edit()
    userInput = timeTextbox.gather()

    durationInSeconds = convertToSeconds(userInput)

    return durationInSeconds

def convertToSeconds(userInput):
    inputParser = re.compile(r"((?P<hours>\d+)h ?)?"
                             r"((?P<minutes>\d+)m ?)?"
                             r"((?P<seconds>\d+)s ?)?"
                             )
    matches = inputParser.search(userInput)
    durationInSeconds = int()

    #NOTE: Input validation needs some more work
    if matches is not None:
       for name, value in matches.groupdict().items():
           if value is not None:
               durationInSeconds += CONVERSION[name] * int(value)

    return durationInSeconds

def formatSeconds(secondsLeft):
    output = str()
    if secondsLeft < 60:
        output = str(secondsLeft) + "s"
    else:
        for period, period_in_seconds in (
                ("h", 3600),
                ("m", 60),
                ("s", 1)
                ):
            if secondsLeft >= period_in_seconds:
                output += str(int(secondsLeft / period_in_seconds))
                output += f"{period}"
                secondsLeft = secondsLeft % period_in_seconds
    output.strip()
    return output

def drawText(stdscr, text):
    y, x = stdscr.getmaxyx()
    inputLines = text.split("\n")
    textWidth = max(map(len, inputLines))
    textHeight = len(inputLines)
    yCenter = int(1/2 * (y - textHeight)) 
    xCenter = int(1/2 * (x - textWidth))
    
    for line in inputLines:
        stdscr.addstr(yCenter, xCenter, line)
        yCenter += 1
    #TODO: catch error if the screen size is too small


def notify(stdscr):
    notificationMessage = ("notify-send " + 
            "--icon=/usr/share/icons/Humanity/apps/16/clock.svg " +
            "-u critical " +
            "'timerpal' " +
            "'Timer is complete!'")
    os.system(notificationMessage)


def countdown(stdscr, timeString):
    '''
    This function provides the main logic for counting down and drawing
    the information to the screen or view
    '''
    duration = int(timeString)
    figler = Figlet(font="univers")

    curses_lock = Lock()
    input_queue = Queue()
    quit_event = Event()

    input_thread = Thread(
            target=inputThreadBody,
            args=(stdscr, quit_event, curses_lock, input_queue)
            )
    input_thread.start()

    syncTime = datetime.now()
    targetTime = datetime.now() + timedelta(seconds=duration)

    secondsLeft = int(ceil((targetTime - datetime.now()).total_seconds()))

    try:
        while secondsLeft > 0:
            stdscr.clear()
            time.sleep(0.01)             # This is to reduce cpu load
            sleepTarget = syncTime + timedelta(seconds=1)
            sleepTarget.replace(microsecond=0)
            now = datetime.now()

            #This handles keypresses listens for a q key press for quit
            #event
            if sleepTarget > now and secondsLeft > 0:
                try:
                    input_action = input_queue.get(True,
                            (sleepTarget - now).total_seconds())
                except Empty:
                    input_action = None
                if input_action == INPUT_EXIT:
                    break

            #1) format secondsLeft to a human readable string
            formattedTime = formatSeconds(secondsLeft)

            #This handles when drawText tries to add a string larger
            #than the window size
            try:
                drawText(stdscr, figler.renderText(formattedTime))
            except curses.error:
                drawText(stdscr, figler.renderText("E"))
            stdscr.refresh()

            syncTime = sleepTarget
            secondsLeft = int(ceil((targetTime - datetime.now()).total_seconds()))

            if secondsLeft <= 0:
                notify(stdscr)
                playsound("/usr/share/sounds/gnome/default/alerts/sonar.ogg")
               #curses.beep()
               # drawText(stdscr, figler.renderText("Done!"))
               # stdscr.refresh()
                break
    finally:
        quit_event.set()
        input_thread.join()
       

def main():
    try:
        stdscr = curses.initscr()
        stdscr.keypad(True)
        curses.noecho() 
        curses.cbreak() 
        curses.curs_set(0)

        invalidInput = True
        while invalidInput is True:
            duration = inputMode(stdscr)
            if duration != 0: 
                invalidInput = False

        countdown(stdscr, duration)
    finally:
        stdscr.keypad(False)
        curses.echo()
        curses.nocbreak() 
        curses.curs_set(1)
        curses.endwin()

if __name__ == "__main__":
    main()
