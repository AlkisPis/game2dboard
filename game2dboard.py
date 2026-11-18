'''
This is a "cleaned" file to by uploaded to https://github.com/mjbrusso/game2dboard and/or added to my form at
https://github.com/AlkisPis/game2dboard
'''

########################################################################################################################

'''
This is a standalone module of 'game2dboard' package the repository if which can be found at
https://github.com/mjbrusso/game2dboard/tree/master/game2dboard
 
It consists of 4 modules: Board.py, Cell.py, ImageMap.py, and outputbar.py, all of which were included in the
'gameedboard' folder of the original package.

Besides the 4 in 1 consolidation, major changes done are listed below:
1) Allowing the setting of a resources path other than the default 'gb_res'.
2) 'set_textcolor()' global function added for getting and setting foreground (text) color for every cell, dynamically
   and individually. 
3) 'cell_bgcolor()' global function added for getting and setting the background color of individual cells. 
4) 'set_textfont()' global function added for setting a general font for every cell, dynamically and individually. 
5) Font name and font weight options added to font size in the 'outputbar.py'.

'''


# Global variables

# Resources folder set in current path by default.
# It can be changed with the function that follows.
resdir = "gb_res" 

# Cell color and font values that can be used by all Classes. 
textcolor = "darkorange" # Default text color
textfont = {"name": "Arial", "size": 14, "attributes": "normal"} # Default text font

# The following functions must be imported together with Board, Label, etc. elements

# Call this to set a path  different that the default one
def set_resdir(path):
  global resdir

  resdir = path

# Set 'clr' in the form "#000000"-#FFFFFF" to set global 'textcolor'
# If not given, the functipn will return the current value of 'textcolor'
def set_textcolor(clr=None):
  global textcolor
  if clr is None: return textcolor
  textcolor = clr

# Set font as a dictionary of the form: 
# {"name": (font name string), "size": (fonr size_integer), "attributes": (font weight and style strings)}
# E.g. {"name": "Times", "size": 14, "attributes": "bold italic"}
def set_textfont(font):
  global textfont

  textfont = font


#The code that follows is the from the original modules. Comments within brackets [] are mine.


### Board.py ###

from tkinter import *
import random
from collections import UserList

class Board(UserList):
  """
  A graphical user interface for 2d arrays (matrix)
  """

  def __init__(
    self,
    nrows,
    ncols):
    """

    Creates an App

    :param int nrows:
      The number of rows.

    :param int ncols:
      The number of columns.
    """

    UserList.__init__(self)             # Initialize parent class
    # Create list [ncols][nrows]
    self.extend([self._BoardRow(ncols, self) for _ in range(nrows)])

    self._nrows = nrows
    self._ncols = ncols
    self._isrunning = False

    # Array used to store cells elements (rectangles)
    self._cells = [[None] * ncols for _ in range(nrows)]

    # The window
    self._root = Tk()
    # cell's container
    self._canvas = Canvas(self._root, highlightthickness=0)
    self._background_image = None           # background image file name
    # rectange for grid color
    self._bgrect = self._canvas.create_rectangle(1, 1, 2, 2, width=0)
    self._bgimage_id = None
    self._msgbar = None                 # message bar component

    # Fields for board properties
    self._title = "game2dboard"             # default window title
    self._cursor = "arrow"                  # default mouse cursor
    self._margin = 5                        # default board margin (px)
    # default grid cell_spacing (px)
    self._cell_spacing = 1
    self._margin_color = "light grey"       # default border color
    self._cell_color = "white"              # default cell color
    self._grid_color = "black"              # default grid color

    self._on_start = None                   # game started callback
    self._on_key_press = None               # user key press callback
    self._on_mouse_click = None             # user mouse callback
    self._on_timer = None                   # user timer callback

    # event
    self._timer_interval = 0            # ms
    self._after_id = None               # current timer id
    self._is_in_timer_calback = False
    # register internal key callback
    self._root.bind("<Key>", self._key_press_clbk)
    # register internal mouse callback
    self._canvas.bind("<ButtonPress>", self._mouse_click_clbk)

  def __getitem__(self, row):             # subscript getter: self[row]
    # Store last accessed row (NOT thread safe... )
    self._BoardRow.current_i = row
    return super().__getitem__(row)     # return a _BoardRow

  # Properties
  # ---------------------------------------------------------------

  @property
  def size(self):
    """

    Number of elements in the array (readonly).

    :type: int
    """
    return self._nrows * self._ncols

  @property
  def nrows(self):
    """

    Number of rows in the array (readonly).

    :type: int
    """
    return self._nrows

  @property
  def ncols(self):
    """

    Number of columns in the array (readonly).

    :type: int
    """
    return self._ncols

  @property
  def width(self):
    """

    Board width, in px. Only available after .show() (readonly).

    :type: int
    """
    return self._root.winfo_reqwidth()

  @property
  def height(self):
    """

    Board height, in px. Only available after .show() (readonly).

    :type: int
    """
    return self._root.winfo_reqheight()

  @property
  def title(self):
    """

    Gets or sets the window title.

    :type: str
    """
    return self._title

  @title.setter
  def title(self, value):
    self._title = value
    self._root.title(value)

  @property
  def cursor(self):
    """

    Gets or sets the mouse cursor shape.<br>
    Setting to None hides the cursor.

    :type: str
    """
    return self._cursor

  @cursor.setter
  def cursor(self, value):
    self._cursor = value
    if value is None:
      value = "none"
    self._canvas.configure(cursor=value)

  @property
  def margin(self):
    """

    Gets or sets the board margin (px).

    :type: int
    """
    return self._margin

  @margin.setter
  def margin(self, value):
    if self._isrunning:
      raise Exception("Can't update margin after show()")
    self._margin = value

  @property
  def cell_spacing(self):
    """
    Gets or sets the space between cells (px).

    :type: int
    """
    return self._cell_spacing

  @cell_spacing.setter
  def cell_spacing(self, value):
    if self._isrunning:
      raise Exception("Can't update cell_spacing after show()")
    self._cell_spacing = value

  @property
  def margin_color(self):
    """
    Gets or sets the margin_color.

    :type: str
    """
    return self._margin_color

  @margin_color.setter
  def margin_color(self, value):
    self._margin_color = value
    self._canvas.configure(bg=value)

  @property
  def cell_color(self):
    """
    Gets or sets cells color

    :type: str
    """
    return self._cell_color

  @cell_color.setter
  def cell_color(self, value):
    self._cell_color = value
    # Update bgcolor for all cells
    if self._isrunning:
      for row in self._cells:
        for cell in row:
          cell.bgcolor = value

  # [Added function - Get/Set individual cell bg color]
  def cell_bgcolor(self, row, col, color=None):
    if not self._isrunning: return
    if color is None: return self._cells[row][col].bgcolor  
    self._cells[row][col].bgcolor = color

  @property
  def grid_color(self):
    """
    Gets or sets grid color

    :type: str
    """
    return self._grid_color

  @grid_color.setter
  def grid_color(self, value):
    self._grid_color = value
    self._canvas.itemconfig(
      self._bgrect, fill=value if not value is None else '')

  @property
  def cell_size(self):
    """
    Gets or sets the cells dimension (width, height)

    :type: int or (int, int)
    """
    return Cell.size

  @cell_size.setter
  def cell_size(self, value):
    if self._isrunning:
      raise Exception("Can't resize cells after run()")
    # size is a tuple (width, height)
    if not type(value) is tuple:
      v = int(value)
      value = (v, v)
    # All cells has same size (class field)
    Cell.size = value

  @property
  def background_image(self):
    """
    Gets or sets the board's background image

    :type: str
    """
    return self._background_image

  @background_image.setter
  def background_image(self, value):
    if self._background_image != value:
      self._background_image = value
      if self._bgimage_id:
        self._canvas.delete(self._bgimage_id)    # clear current image
      if not value is None:
        self.grid_color = self.margin_color = self.cell_color = None
        image = ImageMap.get_instance().load(value)
        if not image is None:
          self._image_object = image
          self._bgimage_id = self._canvas.create_image(  # Draw a image
            0,
            0,
            anchor=NW,
            image=image)
          self._canvas.tag_lower(self._bgimage_id)

  # Private properties
  @property
  def _canvas_width(self):
    return self._ncols * (Cell.width + self.cell_spacing) - self.cell_spacing + (2 * self.margin)

  @property
  def _canvas_height(self):
    return self._nrows * (Cell.height + self.cell_spacing) - self.cell_spacing + (2 * self.margin)

  # Events
  # ---------------------------------------------------------------

  # Game state events
  @property
  def on_start(self):
    """
    Gets or sets the game started callback function.
    The GUI is ready and the program is going to enter the main loop.

    :type: function()
    """
    return self._on_start

  @on_start.setter
  def on_start(self, value):
    self._on_start = value

  # Keyboard events
  @property
  def on_key_press(self):
    """
    Gets or sets the keyboard callback function

    :type: function(key: str)
    """
    return self._on_key_press

  @on_key_press.setter
  def on_key_press(self, value):
    self._on_key_press = value

  # Internal callback
  def _key_press_clbk(self, ev):
    if callable(self._on_key_press):
      self._on_key_press(ev.keysym)

  # Mouse click events
  @property
  def on_mouse_click(self):
    """
    Gets or sets the mouse callback function

    :type: function(button: str, row: int, col: int)
    """
    return self._on_mouse_click

  @on_mouse_click.setter
  def on_mouse_click(self, value):
    self._on_mouse_click = value

  # Internal callback
  def _mouse_click_clbk(self, ev):
    if callable(self._on_mouse_click):
      rc = self._xy2rc(ev.x, ev.y)
      if rc:
        self._on_mouse_click(ev.num, rc[0], rc[1])

  # Timer events
  @property
  def on_timer(self):
    """
    Gets or sets the timer callback function

    :type: function
    """
    return self._on_timer

  @on_timer.setter
  def on_timer(self, value):
    self._on_timer = value

  # internal callback
  def _timer_clbk(self):
    if self._timer_interval > 0 and callable(self._on_timer):
      self._is_in_timer_calback = True
      self._on_timer()              # Call the user callback function
      self._is_in_timer_calback = False
    if self._timer_interval > 0:      # User callback function may change timer!
      self._after_id = self._root.after(
        self._timer_interval, self._timer_clbk)

  # Methods
  # ---------------------------------------------------------------

  def show(self):
    """
    Create the GUI, display and enter the run loop.
    """
    self._setupUI()
    self._isrunning = True
    if callable(self._on_start):
      self._on_start()
    self._root.mainloop()

  def clear(self):
    """

    Clear the board, setting all values to None.
    """
    self.fill(None)

  def close(self):
    """

    Close the board, exiting the program.
    """
    self._root.quit() # [`self._root.destroy()` in GitHub)

  def create_output(self, **kwargs):
    """

    Create a output message bar.
    kwargs:
      color = str
      background_color` = str
      font_size = int
    """
    if self._isrunning:
      raise Exception("Can't create output after run()")
    elif self._msgbar is None:
      self._msgbar = OutputBar(
        self._root, **kwargs)

  def print(self, *objects, sep=' ', end=''):
    """

    Print message to output bar.
    Use like standard print() function.
    """
    if self._msgbar:
      s = sep.join(str(obj) for obj in objects) + end
      self._msgbar.show(s)

  def shuffle(self):
    """

    Random shuffle all values in the board
    """

    # Copy all values to an array, random.shuffle it, then copy back
    a = []
    for r in self:
      a.extend(r)
    random.shuffle(a)
    for row in self:
      for c in range(self._ncols):
        row[c] = a.pop()

  def fill(self, value, row=None, col=None):
    """

    Fill the board (or a row, or a column) with a value

    :param value: The value to store
    :param int row: Index of row to fill. Default=None (all rows)
    :param int col: Index of column to fill. Default=None (all columns)
    """
    if row is None and col is None:         # all rows and columns
      for r in range(self._nrows):
        for c in range(self._ncols):
          self[r][c] = value
    elif not row is None and col is None:  # single row
      for c in range(self._ncols):
        self[row][c] = value
    elif row is None and not col is None:   # a single collumn
      for r in range(self._nrows):
        self[r][col] = value
    else:
      raise Exception("Invalid argument supplied (row= AND col=)")

  def copy(self):
    """
    Returns a shallow copy of the array (only data, not the GUI) into a regular Python list (of lists).
    """
    return [[self[i][j] for j in range(self.ncols)] for i in range(self.nrows)]

  def load(self, data):
    """
    Copy data from regular Python 2D array (list of lists) into the Board.
    """
    if len(data) < self._nrows:
      raise IndexError()
    for r in range(self._nrows):
      if len(data[r]) < self._ncols:
        raise IndexError()
      for c in range(self._ncols):
        self[r][c] = data[r][c]

  def start_timer(self, msecs):
    """

    Start a periodic timer that executes the a function every msecs milliseconds

    The callback function must be registered using .on_timer property.

    :param int msecs: Time in milliseconds.
    """
    if msecs != self._timer_interval:                       # changed
      self.stop_timer()
      self._timer_interval = msecs
      if msecs > 0 and not self._is_in_timer_calback:
        self._after_id = self._root.after(msecs, self._timer_clbk)

  def stop_timer(self):
    """

    Stops the current timer.
    """
    self._timer_interval = 0
    if self._after_id:
      self._root.after_cancel(self._after_id)
      self._after_id = None

  def pause(self, msecs, change_cursor=True):
    """

    Delay the program execution for a given number of milliseconds.

    Warning: long pause freezes the GUI!

    :param int msecs: Time in milliseconds.
    :param bool change_cursor: Change the cursor to "watch" during pause?
    """
    if change_cursor:
      oldc = self.cursor
      self.cursor = "watch"
    self._root.update_idletasks()
    self._root.after(msecs)
    if change_cursor:
      self.cursor = oldc

  # Private methods
  # ---------------------------------------------------------------

  def _setupUI(self):
    # Window is not resizable
    self._root.resizable(False, False)
    self.background_image = self._background_image  # Draw background image
    if not self._background_image is None:
      self.margin_color = self.grid_color = self.cell_color = None
    else:
      self.margin_color = self._margin_color          # Paint background
      self.grid_color = self._grid_color              # Table internal lines
      self.cell_color = self._cell_color              # Cells background

    self.margin = self._margin                      # Change root's margin
    self.cell_spacing = self._cell_spacing          # Change root's padx/y
    self.title = self._title                        # Update window's title
    self.cursor = self._cursor
    self._resize_canvas()
    # Create all cells
    for r in range(self._nrows):
      for c in range(self._ncols):
        x, y = self._rc2xy(r, c)
        newcell = Cell(self._canvas, x, y)
        newcell.bgcolor = self._cell_color
        self._cells[r][c] = newcell
        if self[r][c] != None:                       # Cell has a value
          self._notify_change(r, c, self[r][c])    # show it

    self._canvas.pack()
    self._root.update()

  def _notify_change(self, row, col, new_value):
    if self._cells[row][col] != None:
      self._cells[row][col].value = new_value

  # Config the canvas size
  def _resize_canvas(self):
    self._canvas.config(width=self._canvas_width,
              height=self._canvas_height)

    x1 = y1 = self.margin
    x2 = self._canvas_width - x1
    y2 = self._canvas_height - y1
    self._canvas.coords(self._bgrect, x1, y1, x2, y2)

  # Translate [row][col] to canvas coordinates
  def _rc2xy(self, row, col):
    x = col * (Cell.width + self.cell_spacing) + self.margin
    y = row * (Cell.height + self.cell_spacing) + self.margin
    return (x, y)

  # Translate canvas coordinates to (row, col)
  def _xy2rc(self, x, y):
    # how can i optimize it ???? May be _self.canvas.find_withtag(CURRENT)
    for r in range(self._nrows):
      for c in range(self._ncols):
        cell = self._cells[r][c]
        if cell.x < x < cell.x + Cell.width \
            and cell.y < y < cell.y + Cell.height:
          return (r, c)
    return None

  # Inner classes
  # ---------------------------------------------------------------

  # A row is a list, so I can use the magic function __setitem__(board[i][j])

  class _BoardRow(UserList):
    # Last acessed row (class member).
    # Yes, its not thread safe!
    # Maybe in the future I will use a proxy class
    current_i = None

    def __init__(self, length, parent):
      UserList.__init__(self)
      self.extend([None] * length)         # Initialize the row
      self._parent = parent           # the board

    def __setitem__(self, j, value):
      self._parent._notify_change(self.__class__.current_i, j, value)
      return super().__setitem__(j, value)


### Cell.py ###

from tkinter import *
#import

# Metaclass for Cell
# Implement static class properties
class CellProperties(type):
  @property
  def width(cls):
    """
    Gets cell width
    """
    return cls.size[0]

  @property
  def height(cls):
    """
    Gets cell height
    """
    return cls.size[1]


class Cell(object, metaclass=CellProperties):
  # (w, h: px) Same size for all cells, so it's a static class member
  size = (50, 50)

  def __init__(self, parent, x, y):
    # (5, 5) (77, 5) (149, 5) (5, 77) (77, 77) (149, 77) (5, 149) (77, 149) (149, 149)  Upper left corners in 3x3 bd
    self._image_id = None       # tkinter id from create_image
    self._value = None          # this value
    self._canvas = parent
    self._x = x
    self._y = y
    self._bgcolor = None
    self._text_color = textcolor
    self._id = parent.create_rectangle(
      x,
      y,
      x+Cell.width,
      y+Cell.height,
      width=0
    )

  @property
  def id(self):
    """
    Gets the rectangle id
    """
    return self._id

  @property
  def value(self):
    """
    Gets or sets the cell value.
    """
 
    return self._value

  @value.setter
  def value(self, v):

    if self._value != v:        # Only update when value change
      self._value = v
      if self._image_id:
        self._canvas.delete(self._image_id)    # clear current image
      if not v is None:
        img = ImageMap.get_instance()[v]
        hc = self._x + Cell.width // 2     # horizontal center
        vc = self._y + Cell.height // 2    # vertical center
        # Show image|text @ canvas center
        if img:
          # [Calls TK (g:\python3.10\python~1.amd\lib\tkinter\__init__.py(2817)create_image())]
          self._image_id = self._canvas.create_image(  # Draw image
            hc,
            vc,
            anchor=CENTER,
            image=img)
          a=0  
        else:
          self._image_id = self._canvas.create_text(  # or just draw the value as text
            hc,
            vc,
            anchor=CENTER,
            text=str(v),
            #fill=self._text_color, # [Orig.]
            fill=textcolor,
            font = f"{textfont['name']} {textfont['size']} {textfont['attributes']}",
            width=Cell.width-2)

  @property
  def bgcolor(self):
    """
    Gets or sets the background color.
    """
    return self._bgcolor

  @bgcolor.setter
  def bgcolor(self, value):
    self._bgcolor = value
    self._canvas.itemconfig(self._id, fill=value)   # Change bg color


  @property
  def x(self):
    """
    Gets x coordinate.
    """
    return self._x

  @property
  def y(self):
    """
    Gets y coordinate.
    """
    return self._y


### ImageMap.py ###

import os
import sys
from tkinter import PhotoImage

# A cache to store images

class ImageMap():
  # Singleton Pattern
  __shared_instance = None

  def __init__(self):
    self._dict = {}
    self._imgpath = resdir # r"R:\W\gb_res"

  @classmethod
  def get_instance(cls):                  # Single instance
    # ['cls' = <class 'ImageMap.ImageMap'>]
    if cls.__shared_instance is None:
      cls.__shared_instance = cls()
    return cls.__shared_instance

  def load(self, value):
    fname = os.path.join(self._imgpath, value)
    if not os.path.exists(fname):
      fname += ".png"
      if not os.path.exists(fname):
        return None

    return PhotoImage(file=fname)

  def __setitem__(self, key, value):
    value = str(value)
    if not key in self._dict:
      self._dict[key] = self.load(value) # [Returns the TK image]

  def __getitem__(self, key):
    if not key in self._dict: # [key' = 1]
      self[key] = key       # [self[key] = <tkinter.PhotoImage object at 0x00000135F9B32A40>]
    return self._dict[key]    #  If ;ky; is not in dict the image obhect becomes a number: '1' !!


### outputbar.py ###

from tkinter import *

class OutputBar(Frame):
  def __init__(self, parent, **kwargs):
    color=kwargs.get('color')
    background_color=kwargs.get('background_color')
    font_size=kwargs.get('font_size') or 10
    font_weight=kwargs.get('font_weight') or 'normal' # [Added]
    font_name=kwargs.get('font_name') or 'Arial' # [Added]
    Frame.__init__(self, parent, relief='flat', bg=background_color)
    self.pack(side=BOTTOM, fill=X, expand=True)
    self._label = Label(self, anchor=W,
              fg=color, bg=background_color,
              #font=(None, font_size)) # [Orig]
              font=(font_name, font_size, font_weight)) # [Added 'font_name' and 'font_weight']
    self._label.pack(fill=X, expand=True, padx=2, pady=1)
    #print(f"GBM font_name: {font_name}, font_size: {font_size}, font_weight: {font_weight}") # <<<

  def show(self, value):
    self._label.configure(text=value)


