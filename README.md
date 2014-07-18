pcbdrill
========

Utility to align and correctly scale GCODE for drilling PCB with modified 3d printers by apply matrix correction 


Originally based on code from Alessio Valeri doanloaded from http://www.alessiovaleri.it/using-transform-matrix-for-pcb-drilling-part-2/

The original author has no specified a license and was distributing the utility only by windows and OSX installers. I use Linux.

I asked Alessio permission to public the code, no answer (yet?). 

I've got the original OSX dmg file from Alessio's web site, looked in to it, and discovered the utility was written in python and the pcbdrill.py file was just a source one. The excellon.py was in pyc only, so, i've decompiled it with decompyle2, and then i've done some crappy and fast patches to the original files to better manage GCODE done by using
pcb-gcode.ulp for eagle cad, added a little bit of code to send GCODE commands directly to the 3dprinter over serial, and some other features and fixes.

The code is ugly and pre-alpha quality level, it need probably a complete refactory, but anyway, it works, at leas for me.

Use at your own risk, by downloading it and using it you accept to no comply me for any damage to your 3dprinter, nor in case of your kitten will die, nor in case of you balls will explode in a nuclear blast.

Tested only on debian (sid) using a 3drag 3d printer modified for usage as CNC router with Marlin firmware.
