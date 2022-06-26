import gettext
import os
import re
import sys
import time
import tkinter as tk
import tkinter.filedialog as tkf
import uuid
import webbrowser
from datetime import date, datetime
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *

project_path = os.path.abspath(os.path.dirname(__file__))
data_dir_path = os.path.join(project_path, "data")
xgettext_f_path = os.path.join(data_dir_path, "xgettext_f.txt")
cp_path = os.path.join(data_dir_path, "cp.pkl")