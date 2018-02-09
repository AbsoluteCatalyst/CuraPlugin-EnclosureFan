# Copyright (c) 2018 Pheneeny
# The ScalableExtraPrime plugin is released under the terms of the AGPLv3 or higher.

import os, json, re

from UM.Extension import Extension
from UM.Application import Application
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Logger import Logger

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("DefaultTemperatureOffset")


class PrintTemperatureOffset(Extension):
    def __init__(self):
        super().__init__()

        self._application = Application.getInstance()

        self._i18n_catalog = None

        self._fan_on_key = "enclosure_fan_on"
        self._fan_on_dict = {
            "label": "Fan On Command",
            "description": "Command to issue to turn fan on. This will depend on your firmware and configuration. For Marlin, 'M106 P1' will usually enable the second fan defined. For smoothieware, you can define the M code or subcode to control a fan, such as M106.1",
            "type": "string",
            "unit": "",
            "default_value": "M106 P1",
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }
        self._post_printing_speed_key = "enclosure_fan_post_print_speed"
        self._post_printing_speed_dict = {
            "label": "After Printing Complete Speed",
            "description": "Speed to set enclosure fan to after printing has completed",
            "type": "float",
            "unit": "%",
            "default_value": 0,
            "minimum_value": 0,
            "maximum_value": 100,
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        self._printing_speed_key = "enclosure_fan_printing_speed"
        self._printing_speed_dict = {
            "label": "Speed While Printing",
            "description": "Speed to set enclosure fan to while printing",
            "type": "float",
            "unit": "%",
            "default_value": 0,
            "minimum_value": 0,
            "maximum_value": 100,
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False
        }
        self._setting_key = "enclosure_fan_enable"
        self._setting_dict = {
            "label": "Enable Enclosure Fan",
            "description": "Control an enclosure fan with the generated gcode. Allows you to set a fan speed while printing, and a fan speed for after the print has completed.",
            "type": "bool",
            "unit": "",
            "default_value": False,
            "settable_per_mesh": False,
            "settable_per_extruder": False,
            "settable_per_meshgroup": False,
        }
        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)

        self._application.globalContainerStackChanged.connect(self._onGlobalContainerStackChanged)
        self._onGlobalContainerStackChanged()

        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)


    def _onContainerLoadComplete(self, container_id):
        container = ContainerRegistry.getInstance().findContainers(id=container_id)[0]
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        self.create_and_attach_setting(container, self._setting_key, self._setting_dict, "material")
        self.create_and_attach_setting(container, self._printing_speed_key, self._printing_speed_dict, self._setting_key)
        self.create_and_attach_setting(container, self._post_printing_speed_key, self._post_printing_speed_dict, self._setting_key)
        self.create_and_attach_setting(container, self._fan_on_key, self._fan_on_dict, self._setting_key)

    def _onGlobalContainerStackChanged(self):
        self._global_container_stack = self._application.getGlobalContainerStack()

    def _filterGcode(self, output_device):

        scene = self._application.getController().getScene()
        # get settings from Cura

        enclosure_fan_enabled = self._global_container_stack.getProperty(self._setting_key, "value")
        printing_fan_speed = self._global_container_stack.getProperty(self._printing_speed_key, "value")
        post_printing_fan_speed = self._global_container_stack.getProperty(self._post_printing_speed_key, "value")
        fan_on_command = self._global_container_stack.getProperty(self._fan_on_key, "value").strip()

        if not fan_on_command:
            return;

        post_print_command = fan_on_command + " S" + str(post_printing_fan_speed)
        print_command = fan_on_command + " S" + str(printing_fan_speed);

        if not enclosure_fan_enabled:
            return

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict:  # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return


        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]
            if len(gcode_list) < 2:
                Logger.log("w", "Plate %s does not contain any layers", plate_id)
                continue

            if ";Enclosure Fan" not in gcode_list[1]:
                #TODO
                gcode_dict[plate_id] = gcode_list
            else:
                Logger.log("d", "Plate %s has already been processed", plate_id)
                continue

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



