Main 4 files are,
-loader.py (is the base loader)
-command_factory.py (main brain)
-anime_service.py (main anime brain)
-commands.json (file to add to modify or add new commands ie features)

Rest of the files are "examples".

when your adding in your own commands, it must look like this as example,

class FeatureName:
    requires_api = False
    requires_parameter = False
    requires_username = False

if your script is getting errors or api errors, its because currently if its not marked as false it means its true.
(ill fix this later)


if you want to add your own what you have to do is,
-Drop .py file in same folder as it
-open commands.json and add the new feature there
-open features.txt add it there
-Win!