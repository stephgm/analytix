#!/bin/bash

pyinstaller --clean --paths /home/hollidayh/Hamilton/src/analytix/modules --add-data 'adarConfigurator.ui:.' adarConfigurator.py
