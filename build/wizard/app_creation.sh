#!/bin/bash

echo "Welcome to the app creation wizard"

RED='\033[0;31m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
APP_TYPES=("p5js" "threejs" "empty")

# Set app_name to empty string
app_name=""

# Verify that the user is in the gosai directory
if [[ ! -d "../gosai" ]]; then
    echo -e "${RED}Error${NC}: You must be in the gosai directory to run this script"
    exit 1
fi

# Verify that the home directory exist
if [[ ! -d "./home" ]]; then
    echo -e "${RED}Error${NC}: The home directory does not exist"
    echo -e "${ORANGE}Note${NC}: Run the platform creation wizard to create the home directory or clone an existing platform"
    exit 1
fi

app_name_set=false
# While app_name is empty string or already exist, ask the user for the name of the app
while [[ ! "$app_name_set" = true ]]; do
    echo
    read -p "Enter the name of the app you want to create: " app_name
    app_name=$(echo $app_name | tr '[:upper:]' '[:lower:]')
    app_name=$(echo $app_name | tr '-' '_')
    app_name=$(echo $app_name | tr ' ' '_')
    app_name=$(echo $app_name | sed 's/[^a-zA-Z0-9_]//g')
    if [[ $app_name == "" ]]; then
        echo -e "${RED}Error${NC}: App name cannot be empty"
    elif [[ -d "./home/apps/$app_name" ]]; then
        echo -e "${RED}Error${NC}: $app_name already exist"
    else
        app_name_set=true
    fi
done

echo
echo "Select the template of the app you want to create:"
for i in "${!APP_TYPES[@]}"; do
    echo "$i) ${APP_TYPES[$i]}"
done
echo -e "${ORANGE}Note${NC}: If you are not sure, select p5js"

# Ask the user for the type of app
app_type=""
app_type_set=false
while [[ ! "$app_type_set" = true ]]; do
    echo
    read -p "Enter the number of the template app you want to create: " app_type
    if [[ $app_type == "" ]]; then
        echo -e "${RED}Error${NC}: App template cannot be empty"
    elif [[ ! $app_type =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error${NC}: App template must be a number"
    elif [[ $app_type -lt 0 || $app_type -ge ${#APP_TYPES[@]} ]]; then
        echo -e "${RED}Error${NC}: App template must be between 0 and $(( ${#APP_TYPES[@]} - 1 ))"
    else
        app_type_set=true
    fi
done

# Create the app folder
mkdir "./home/apps/$app_name"

# Copy the processing.py to the app folder
cp -r "./build/wizard/templates/app/processing.py" "./home/apps/$app_name/processing.py"

# Copy either display_none.js, display_p5js.js or display_threejs.js to the app folder
if [[ ${APP_TYPES[$app_type]} == "empty" ]]; then
    cp -r "./build/wizard/templates/app/display_none.js" "./home/apps/$app_name/display.js"
elif [[ ${APP_TYPES[$app_type]} == "p5js" ]]; then
    cp -r "./build/wizard/templates/app/display_p5.js" "./home/apps/$app_name/display.js"
elif [[ ${APP_TYPES[$app_type]} == "threejs" ]]; then
    cp -r "./build/wizard/templates/app/display_three.js" "./home/apps/$app_name/display.js"
fi

# Replace all instances of "template_app" in display.js and processing.py with the app_name
sed -i "s/template_app/$app_name/g" "./home/apps/$app_name/display.js"
sed -i "s/template_app/$app_name/g" "./home/apps/$app_name/processing.py"

echo
echo -e "App $app_name created ${GREEN}successfully${NC} with template ${APP_TYPES[$app_type]}"
