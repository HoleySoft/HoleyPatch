# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='PySential',
    python_requires='>3.8.3',
    version='0.1',
    packages=['pysential'],
    url='',
    license='',
    author='Florian L. R. Lucas',
    author_email='info@protolyse.com',
    description='',
    install_requires=[
        'PySide2',
        'qimage2ndarray',
        'shiboken2',
        'openpyxl',
        'numpy',
        'scipy',
        'pyqtgraph-qp',
        'pyautogui',
        'Pillow',
        'opencv-python',
    ],
)
