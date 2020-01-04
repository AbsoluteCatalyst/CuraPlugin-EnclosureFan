
### Note! This script isn't exactly the same as the parent repo's! 
#### I originally made this script sometime around April 2019 but I unfortunately can't remember if I used  [Pheneeny's](https://github.com/Pheneeny) [CuraPlugin-ScalableExtraPrime](https://github.com/Pheneeny/CuraPlugin-ScalableExtraPrime) as a base to start off with and coincidentally stumbled upon their own enclosure fan plugin recently OR if I actually used their EnclosureFan plugin as a base at the time instead, as silly as that sounds.<br/><br/>In which case just to be safe, I've forked their EnclosureFan plugin and credit goes to them!

<font size="+3"><b>How it works:<font/></b> 
---
This plugin uses two special preprocessing tokens you can put in your own Start and End G-code!

> ;EN_FAN_START_MARKER

and
 
>;EN_FAN_END_MARKER

Both of these are markers that indicate *where* the plugin should place the generated initial/ending fan speed G-code. 

Here's an example of my Start G-code:
<pre><code>M104 S{material_print_temperature_layer_0} T0 F1
M140 S{material_bed_temperature_layer_0}
G90 ; SET ABSOLUTE POSITIONING
G28 ; HOME
M116 ; WAIT FOR HEAT
<b>;EN_FAN_START_MARKER</b>

M530 S1 ; SET PRINTING
</code></pre>
And my final cura G-code output: 
<pre><code>M104 S210 T0 F1
M140 S50
G90 ; SET ABSOLUTE POSITIONING
G28 ; HOME
M116 ; WAIT FOR HEAT
;EN_FAN_START_MARKER
<b>M106 P2 S38 ; SET ENCLOSURE FAN 2 BEGIN
M106 P1 S63 ; SET ENCLOSURE FAN 1 BEGIN</b>

M530 S1 ; SET PRINTING 
</code></pre>

Omitting these markers will simply place the generated fan G-code at the beginning of your Start G-code and at the end of your End G-code, respectively.

- <font size="+1"><b>For now this plugin only utilizes standard M106 P\<number> S\<speed> G-code commands, with one additional ~~custom~~ parameter; O\<delay>, for the fan timeouts (If used).<font/></b>
<font size="+0"><i>~~(Sadly this custom O parameter only works for me as it doesn't exist in popular firmwares right now! Hopefully someday it; or a variant thereof, will!)~~ Added in Repetier V2 firmware.</i></b><font/>
  
## Adds the following options to your Cura's Cooling setting panel:
![Options](https://i.imgur.com/U8hFqxY.png)

<dl>
<dt>Enclosure Fans:</dt>
<dd>Toggle the plugin on/off. </dd><br>

<dt>Enclosure Fan Number(s):</dt> 
<dd>These are the fan numbers this plugin will create G-code for. ("M106 P&lt;number>")</dd>
<dd><b><font size="+0">You can either use a single lone number for a single fan, or a comma separated list of multiple fan numbers as shown above. The plugin will write G-code for each.</font></b></dd><br>

<dt> Initial Enclosure Fan Speed(s):</dt> 
<dd>Sets the fan speeds for the start and entirety of the print. Values are in percentage, 0% - 100% and set 0 to disable.</dd>
<dd><b><font size="+0">Similar to before, you may use a number or list. Each speed is tied to their respective fan number in the same order!</b><dd>
<dd><b><font size="+0">If you have more fan numbers than you have speeds, the LAST speed in the list will be applied to the remaining fan numbers!)</b><dd><br>

<dt> Ending Enclosure Fan Speed(s):</dt> 
<dd>Sets the fan speeds at the end of the print. Values are in percentage, 0% - 100% and set 0 to disable.</dd>
<dd><b><font size="+0">The same list input options and caveats from above apply.</b><dd><br>
  
<dt> Ending Enclosure Fan Timeout(s):</dt> 
<dd>Sets the time in seconds for a custom M106 parameter "O",  to turn off the fans after said time. Set 0 to disable.</dd>
<dd><b><font size="+0">The same list input options and caveats from above apply.</b><dd>
<dd><b><font size="+1"><strike>Won't function in most firmwares.</strike> Only supported in Repetier V2 firmware at the moment. Set to 0 by default.</b><dd>
</dl>

<font size="+3"><b>Installation:<font/></b> 
---

 1. Download this repository as a ZIP.
 2. Navigate to your Ultimaker Cura plugin directory ( eg. C:\Program Files\Ultimaker Cura 4.3\plugins\ )
 3. Extract/Drop the "CuraPlugin-EnclosureFan-master" folder from the previously downloaded zip file into the plugin directory. 
 4. Restart Cura if it's open.

If everything works, you should see "Enclosure Fans" appear in your cooling settings tab. 


<font size="+3"><b>- Last tested to work on Cura 4.3.0<font/></b>  