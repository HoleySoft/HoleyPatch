
import glob
import tempfile
import shutil
import logging
logger = logging.getLogger(__name__)


class ImageManager:
    """A class used to load images from different file location(s) or packages.

    Attributes
    ----------
    root_dir : list
        List object containing all root directories to check
    temp_dicts
        Container for temporary dirs

    Methods
    ----------
    add_root(root_dir)
        Add new root_dir location
    load_package(filename)
        Creates new temporary dir, unpacks the package and saves in temporary dir
    get_image(filename)
        Scans all root_dir(s) for match, returns first match
    _check_dict(root_dir, filename)
        Check the root_dir for filename
    """
    def __init__(self):
        self.root_dir = []
        self.temp_dicts = []

    def add_root(self, root_dir):
        """Add new root_dir location

        Parameters
        ----------
        root_dir : str
            Location of directory containing images
        """
        self.root_dir.append(root_dir)

    def load_package(self, filename):
        """Creates new temporary dir, unpacks the package and saves in temporary dir

        Parameters
        ----------
        filename : str
            Location of package containing images to unpack
        """
        self.temp_dicts.append(tempfile.TemporaryDirectory(suffix='pysential'))
        shutil.unpack_archive(filename, self.temp_dicts[-1].name)
        root_dir = self.temp_dicts[-1].name + "/*/"
        self.add_root(root_dir)

    def get_image(self, filename=''):
        """Scans all root_dir(s) for match, returns first match

        Parameters
        ----------
        filename : str
            The filename of the image to check

        Returns
        -------
        result
        """
        for root in self.root_dir:
            result = self._check_dict(root, filename)
            if result:
                return result
        return filename

    @ staticmethod
    def _check_dict(root_dir, filename):
        """Check the root_dir for filename

        Parameters
        ----------
        root_dir : str
            Root dir to crawl
        filename : str
            The filename of the image to check

        Returns
        -------
        path : str:
            Path to matching image
        """
        paths = glob.glob(filename)
        if len(paths) == 0:
            paths = glob.glob(root_dir + '/' + filename)
        if len(paths) == 0:
            paths = glob.glob(root_dir + '/**/' + filename)
        if len(paths) == 0:
            paths = glob.glob(filename + '.*')
        if len(paths) == 0:
            paths = glob.glob(root_dir + '/' + filename + '.*')
        if len(paths) == 0:
            paths = glob.glob(root_dir + '/**/' + filename + '.*')
        try:
            return paths[0]
        except IndexError:
            return None
