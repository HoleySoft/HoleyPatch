
import threading


class AbstractThread(threading.Thread):
    """
    A class used to represent an abstract thread.


    Attributes
    ----------
    func : object
        Function object to be called within the thread loop
    arguments
        Arguments to be passed to func
    recurrent : boolean
        If true, keep thread running in a background loop until stopped
    active : boolean
        If recurrent is true, active can deactivates the background loop

    Methods
    ----------
    run() -> None
        Start the thread, loop if recurrent and active
    stop() -> None
        Sets active to False
    """

    def __init__(self, parent: object, func=None, arguments=None, recurrent=False) -> None:
        """Adds new menu bar options

        Parameters
        ----------
        parent : object
            Parent object to attach the thread to; can be AbstractModule or AbstractWidget
        func : object
            Function object to be called within the thread loop
        arguments
            Arguments to be passed to func
        recurrent : boolean
            If true, keep thread running in a background loop until stopped

        Returns
        -------
        None
        """
        threading.Thread.__init__(self)
        self.parent = parent
        if hasattr(self.parent, 'win'):
            self.parent = parent.win
        self.func = func
        self.arguments = arguments
        self.recurrent = recurrent
        self.active = False

    def run(self) -> None:
        """Run the current thread

        Returns
        -------
        None
        """
        run = True
        self.active = True
        if self.func:
            while run and self.active:
                run = self.recurrent
                if not self.parent.is_alive:
                    run = False
                if self.arguments:
                    self.func(self.arguments)
                else:
                    self.func()
            self.stop()

    def stop(self) -> None:
        """Stop thread loop if recurrent is True

        Returns
        -------
        None
        """
        self.active = False
