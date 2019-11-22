from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.i18n import i18nCatalog
from UM.Preferences import Preferences
from UM.Logger import Logger

i18n_catalog = i18nCatalog("EnclosureFans") 
class EnclosureFans(Extension):
    def __init__(self):
        super().__init__()
 
        self._application = Application.getInstance()
        self._i18n_catalog = None
         
        self._fan_end_delay_key = "enclosure_fan_end_delay"
        self._fan_end_delay_dict = {
            "label": "Ending Enclosure Fan Timeout(s)",
            "description": "How long to keep the enclosure fan turned on for after a print. (Uses firmware dependant \"O<seconds>\" parameter)",
            "type": "[int]",
            "unit": "s",
            "default_value": 120,
            "minimum_value": 0,
            "enabled": "enclosure_fan_enabled",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        
        self._fan_end_key = "enclosure_fan_end_speed"
        self._fan_end_dict = {
            "label": "Ending Enclosure Fan Speed(s)",
            "description": "Speed of the enclosure fan once the print is done.\nSet to 0 to turn off your enclosure fan at the end of the print.",
            "type": "[int]",
            "unit": "%",
            "default_value": 100,
            "minimum_value": 0,
            "maximum_value": 100,
            "enabled": "enclosure_fan_enabled",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        } 
        
        self._fan_begin_key = "enclosure_fan_begin_speed"
        self._fan_begin_dict = {
            "label": "Initial Enclosure Fan Speed(s)",
            "description": "Speed of the enclosure fan right as a print begins and throughout the print itself.\nSet to 0 for no enclosure fan during print.",
            "type": "[int]",
            "unit": "%",
            "default_value": 25,
            "minimum_value": 0,
            "maximum_value": 100,
            "enabled": "enclosure_fan_enabled",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        
        self._fan_num_key = "enclosure_fan_num"
        self._fan_num_dict = {
            "label": "Enclosure Fan Number(s)",
            "description": "Specific firmware number of the fan itself, (eg. '0' is your cooling fan, and '1' is your enclosure fan.)",
            "type": "[int]",
            "default_value":"[1]",
            "enabled":"enclosure_fan_enabled",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        
        self._setting_key = "enclosure_fan_enabled"
        self._setting_dict = {
            "label": "Enclosure Fans",
            "description": "Turns on enclosure fans to provide ventilation/airflow for low temperature materials.",
            "type": "bool",
            "default_value": False, 
            "settable_per_mesh": False,
            "settable_per_extruder": False, 
            "settable_per_meshgroup": False
        }
        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

        self._application.globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
        self._onGlobalContainerStackChanged()

        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode) 
        
        
    def _onGlobalContainerStackChanged(self):
        self._global_container_stack = self._application.getGlobalContainerStack()
        
       
    def _onContainerLoadComplete(self, container_id):
        container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
        
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return
 
        # Enabled
        self.create_and_attach_setting(container, self._setting_key, self._setting_dict, "cooling")        
        # Fan number
        self.create_and_attach_setting(container, self._fan_num_key, self._fan_num_dict, "cooling")
        # # Fan starting speed
        self.create_and_attach_setting(container, self._fan_begin_key, self._fan_begin_dict, "cooling")
        # # Fan ending speed
        self.create_and_attach_setting(container, self._fan_end_key, self._fan_end_dict, "cooling")
        # # Fan ending timeout
        self.create_and_attach_setting(container, self._fan_end_delay_key, self._fan_end_delay_dict, "cooling")

            

    def _filterGcode(self, output_device):
        scene = self._application.getController().getScene()
        
        enclosure_fan_enabled  =    self._global_container_stack.getProperty(self._setting_key, "value")
        if not enclosure_fan_enabled:
            return
        
        enclosure_fan_num_list =                 (self._global_container_stack.getProperty(self._fan_num_key, "value")).replace(" ", "").strip('][').split(',') 
        if not enclosure_fan_num_list:
            return
            
        remove_dupe = []
        for i in enclosure_fan_num_list:
            if i not in remove_dupe and i: 
                remove_dupe.append(i)
                
        enclosure_fan_num_list = remove_dupe 
        
        enclosure_fan_begin_speed =               self._global_container_stack.getProperty(self._fan_begin_key, "value")
        if type(enclosure_fan_begin_speed) is not int: 
            enclosure_fan_begin_speed = enclosure_fan_begin_speed.replace(" ", "").strip('][').split(',')
        
        enclosure_fan_end_speed =                 self._global_container_stack.getProperty(self._fan_end_key, "value")
        if type(enclosure_fan_end_speed) is not int: 
            enclosure_fan_end_speed = enclosure_fan_end_speed.replace(" ", "").strip('][').split(',') 
        
        enclosure_fan_end_delay =                 self._global_container_stack.getProperty(self._fan_end_delay_key, "value")
        if enclosure_fan_end_delay and type(enclosure_fan_end_delay) is not int: 
            enclosure_fan_end_delay = enclosure_fan_end_delay.replace(" ", "").strip('][').split(',')
         
        
        
        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict: # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return
     
     
        for index, enclosure_fan_num in enumerate(enclosure_fan_num_list): 
         
            if int(enclosure_fan_num) < 0: 
                continue 
                
            if isinstance(enclosure_fan_begin_speed, list):
                begin_speed = int(enclosure_fan_begin_speed[index if index < len(enclosure_fan_begin_speed) else -1])
            else:
                begin_speed = int(enclosure_fan_begin_speed)
                
            if isinstance(enclosure_fan_end_speed, list):
                end_speed = int(enclosure_fan_end_speed[index if index < len(enclosure_fan_end_speed) else -1])
            else:
                end_speed = int(enclosure_fan_end_speed)
            
            if isinstance(enclosure_fan_end_delay, list):
                end_delay = enclosure_fan_end_delay[index if index < len(enclosure_fan_end_delay) else -1]
            else: 
                end_delay = enclosure_fan_end_delay 
                 
            begin_speed =               max(min(int((begin_speed / 100.0) * 255.0), 255), 0)
            end_speed =                 max(min(int((end_speed / 100.0) * 255.0), 255), 0)
        
            begin_fan_command = "M106 P"+enclosure_fan_num + " S" + str(begin_speed) + " ; SET ENCLOSURE FAN " + enclosure_fan_num + " BEGIN"
            end_fan_command  =  "M106 P"+enclosure_fan_num + " S" + str(end_speed) + " ; SET ENCLOSURE FAN " + enclosure_fan_num + " END\n"
            
            fan_delay_command = "" 
            if end_delay:
                fan_delay_command = "M106 P" + enclosure_fan_num + " S0 O" + str(end_delay) + " ; SET ENCLOSURE FAN " + enclosure_fan_num + " END TIMEOUT"
                

            dict_changed = False

            # plate_id is for "seperate build plates".
            for plate_id in gcode_dict:
                gcode_list = gcode_dict[plate_id]
                if len(gcode_list) < 2:
                    Logger.log("w", "Plate %s does not contain any layers", plate_id)
                    continue 
                    
                 
                # TODO: just split the start/end layers once and then insert the commands for every fan num. 
                
                start_layer = gcode_list[1].split("\n")
                if len(start_layer) == 0:
                    start_layer.append("")
                  
                # Search the first block of gcode (ends up being printer start gcode)
                # and replaces a start marker if found
                if ';EN_FAN_START_MARKER' in start_layer: 
                    start_marker = start_layer.index(";EN_FAN_START_MARKER") + 1
                    start_layer.insert(start_marker if start_marker < len(start_layer) else -1, begin_fan_command)
                else:
                    start_layer.insert(0, begin_fan_command)
                    
                gcode_list[1] = "\n".join(start_layer)
                 
                
                          
                last_layer = gcode_list[-1].split("\n") 
                if ';EN_FAN_END_MARKER' in last_layer:
                    end_marker = last_layer.index(";EN_FAN_END_MARKER") + 1 
                    last_layer.insert(end_marker if end_marker < len(last_layer) else -1, " ") 
                    last_layer.insert(end_marker if end_marker < len(last_layer) else -1, (end_fan_command + fan_delay_command)) 
                else: 
                    last_layer.insert(0, end_fan_command + fan_delay_command)
                     
                
                gcode_list[-1] = "\n".join(last_layer)  
                
                gcode_dict[plate_id] = gcode_list
                dict_changed = True 
                    
                if dict_changed:
                    setattr(scene, "gcode_dict", gcode_dict)
                    
                    
                    
            
    def create_and_attach_setting(self, container, setting_key, setting_dict, parent):
        parent_category = container.findDefinitions(key=parent)
        definition = container.findDefinitions(key=setting_key)
        if parent_category and not definition:
            # this machine doesn't have a scalable extra prime setting yet
            parent_category = parent_category[0]
            setting_definition = SettingDefinition(setting_key, container, parent_category, self._i18n_catalog)
            setting_definition.deserialize(setting_dict)

            parent_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition
            container._updateRelations(setting_definition)
            
            
        