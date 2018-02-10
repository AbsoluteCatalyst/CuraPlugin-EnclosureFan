# CuraPlugin-EnclosureFan
A Cura plugin to control an enclosure exhaust fan

### Settings

##### Enable Enclosure Fan 
* Set to true to have the gcode control your enclosure fan. If set to false, no enclosure fan control commands will be issued  

##### Speed While Printing
* The speed the fan will run at while the printer is warming up the hotend/bed and while it is printing. Speed is set from 0% - 100%

##### Speed After Printing Complete
* The speed the fan will run at after all printing has completed and the machine is cooling down. Speed is set from 0% - 100%

##### Fan On Commnad
* The command to be issued to turn the fan on. Output will be in the following format: [Fan On Command] S[Fan Speed]. The fan on command will be firmware and configuration dependent. For example, Marlin addresses additional fans with M106 P[Fan Number] S[Fan Speed], so to use Fan 1 as an enclosure fan, set Fan On Command to "M106 P1". Smoothieware allows a subcode to be used, so an example value may be "M106.1"

### Why?
An enclosure exhaust fan removes fumes, but it will also remove heat from the enclosure. So for materials that like a heated enclosure(like ABS), it may be helpful to slow the enclosure fan down while printing to maintain heat, but then turn the fan on full after printing is complete to eject any remaining fumes.





