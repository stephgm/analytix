#!/bin/bash

#pyinstaller --clean --paths /home/hollidayh/Hamilton/src/analytix/modules --add-data 'adarConfigurator.ui:.' adarConfigurator.py

# cx Freeze
if [ -e build ];then
rm -rf build
fi
/storage/data/local/bin/python -OO setup.py build
cat > build/exe.linux-x86_64-3.7/run << EOF
#!/bin/bash

export LD_LIBRARY_PATH="/storage/data/local/lib:/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib"
#export LD_LIBRARY_PATH=".:/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib"

./adarConfigurator
EOF
chmod +x build/exe.linux-x86_64-3.7/run
