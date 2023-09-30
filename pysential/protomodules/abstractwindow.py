
from ..gui.widgets import Widgets


class AbstractWindow(Widgets):
    """
    A class used to represent an abstract window.


    Attributes
    ----------
    obj : object
        Parent object
    widgets : Widgets
        Widget manager
    show : boolean
        A boolean describing whether to show on initiation
    title : str
        A string describing the title of the module
    ico : str
        File location of the icon to show on module
    win : object
        Container for the window

    Methods
    ----------
    set_content
        Attached content to container win
    set_title(title='')
        Sets the title of the window
    run
        This function is called upon start and should be redefined to add elements
    close
        Invoke to close the window
    """

    def __init__(self, obj: object, title='') -> None:
        """
        Parameters
        ----------
        obj : object
            Parent object
        title : str
            Window title
        """
        super(AbstractWindow, self).__init__(obj)
        self.obj = obj
        self.ico = "logo"
        self.title = title
        self.show = True
        self.win = self.new_window()
        self.widgets = Widgets(self.obj)
        self.widgets.set_parent(self.win)

    def set_content(self) -> None:
        """Set content of current window
        """
        self.win = self.widgets.set_content(self.win)
        self.widgets.show_window(self.win)

    def set_title(self, title='') -> None:
        """Sets the title of the window
        Parameters
        ----------
        title : str
            Window title
        """
        self.title = title

    def run(self) -> None:
        """Method to run upon call
        """
        self.widgets.set_content(self.win)

    def close(self):
        """Method to close the window
        """
        #  TODO: Check this function
        self.win.close()

