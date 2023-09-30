"""
This script contains the basic elements required to show the gui.
All functions contained here, should have a counterpart in the gui package/wrapper.
"""

import logging
logger = logging.getLogger(__name__)


class Elements:
    """A class containing all essential element widgets that connect to the GUI module

    Attributes
    ----------
    obj : object
        Parent object
    widgets : object
        Graphical User Interface module with compatible widget objects

    Methods
    ----------
    make_button(function_connect=None, arguments=None, text='', border=True, img='', grid=None, parent=None)
        text
    make_label(text="", grid=None, parent=None)
        text
    media_feed(grid=None, parent=None)
        text
    media_area(grid=None, parent=None)
        text
    set_content(parent)
        text
    """
    def __init__(self, obj: object):
        self.obj = obj
        self.widgets = obj.gui_module

    def make_button(self, function_connect=None, arguments=None,
                    text='', border=True, img='', grid=None, parent=None) -> object:
        """Returns a button compatible widget object

        Parameters
        ----------
        function_connect : object
            Function to connect upon press down
        arguments
            Arguments to pass to function_connect
        text : str
            Text to be displayed over the button
        img : str
            File location of image to display over button
        border : boolean
            Display with or without border (True/False)
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        img = self.obj.image_manager.get_image(img)
        return self.widgets.make_button(parent, function_connect=function_connect,
                                        arguments=arguments, text=text, border=border, img=img, x=x, y=y, dx=dx, dy=dy)

    def make_label(self, text="", grid=None, parent=None) -> object:
        """Return a label compatible widget object

        Parameters
        ----------
        text : str
            Text to display in the label
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.make_label(parent, x=x, y=y, dx=dx, dy=dy, text=text)

    def media_feed(self, grid=None, parent=None):
        """Return a media_feed widget object, see GUI module

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        return self.widgets.media_feed(parent, x=x, y=y, dx=dx, dy=dy)

    def media_area(self, grid=None, parent=None):
        """Return a media_area widget object, see GUI module

        Parameters
        ----------
        grid : tuple
            Tuple containing the grid as (X0,X1, Y0, Y1)
        parent :  object
            Parent object to attach widget too
        Returns
        -------
        object
        """
        x, y, dx, dy = self._get_grid(grid)
        if not parent:
            parent = self.parent
        try:
            return self.widgets.media_area(self.parent, x=x, y=y, dx=dx, dy=dy)
        except AttributeError as e:
            logger.error(e, exc_info=True)

    def set_content(self, parent):
        """Sets the widget content of parent

        Parameters
        ----------
        parent :  object
            Parent object with attached widgets
        Returns
        -------
        object
        """
        if not parent:
            parent = self.parent
        return self.widgets.set_content(parent)
