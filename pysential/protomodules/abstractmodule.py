
from ..gui import Widgets


class AbstractModule:
    """
    A class used to represent an abstract module.


    Attributes
    ----------
    obj : object
        Parent object
    widgets : Widgets
        Widget manager
    menu_bar : list
        A list containing all the menu bar children
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
    new_window(win: object)
        Register new window and set is as current container win
    set_content
        Attached content to container win
    add_menu(parent: str, child: str, function: object, args=None) -> None
        Add menu item to parent menu with child name and function, passes arguments from args
    run(win: object)
        This function is called upon start and should be redefined to add elements
    """

    def __init__(self, obj: object) -> None:
        """
        Parameters
        ----------
        obj : object
            Parent object
        """
        self.obj = obj
        self.widgets = Widgets(self.obj)
        self.menu_bar = []

        # Parameter that tells if the module should be displayed on starting the application
        self.show = False
        self.title = ""
        self.ico = "logo"
        self.win = None

    def new_window(self, win: object) -> None:
        """Create a new window for the module

        Parameters
        ----------
        win : object
            Parent window object
        """
        self.win = win
        self.widgets.set_parent(self.win)

    def set_content(self):
        """Set content of current window
        """
        self.win = self.widgets.set_content(self.win)

    def add_menu(self, parent: str, child: str, function: object, args=None) -> None:
        """Adds new menu bar options

        Parameters
        ----------
        parent : str
            The name of the parent menu
        child : str
            Child name, e.g. text displayed on menu option
        function : object
            The function to be triggered on user submit
        args
            Arguments to be passed to the function, default=None

        Returns
        -------
        None
        """
        item = (parent, child, function, args,)
        self.menu_bar.append(item)

    def run(self, win: object) -> None:
        """Method to run upon call

        Parameters
        ----------
        win : object
            Parent window object
        """
        self.new_window(win)
        self.set_content()
