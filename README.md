
# HoleyPatch

## How to run
First use: Run `setup.py` contained in the `pysential` using Python 3.7 or newer to install dependencies.

Starting the software: Run `main.py` contained in the `pysential` folder Python 3.7 or newer to run the GUI.  

## How to use
HoleyPatch allows the viewing of HEKA files.
To open a file, place the .dat file via drag-and-drop onto the GUI. If simultaneous recordings are present, they will be displayed as Imon-n under a Series. By clicking an individual pulse, the trace and its corresponding IV-plot will be displayed.
To change the digital filter frequency, use the first button.
To display a cursor for time and amplitude, use the second button. 
To zoom-in, click-and-hold the cursor on x- or y-axis.
Zo zoom-out, use right-click and “View All” or double-click.
To export a trace, right-click on a trace. 

## Adapting the software
The `pysential` wrapper opens the modules from `main.py`. You can load and/or modify the modules with the `app.add_module(ModuleName)` handler in the main loop.
The `HoleyPatch` module is contained in `./pysential/electrophys_module/ePhysModule.py`.

New modules can be created using the template as shown in `./pysential/template_module.py`.

## Authors and acknowledgements
#### Main contributors
* [Florian L. R. Lucas](http://orcid.org/0000-0002-9561-5408 "Orcid page")
* [Carsten Wloka](https://orcid.org/0000-0003-0487-3311 "Orcid page")

## License
HoleyPatch is distributed under BSD-3 Clause
