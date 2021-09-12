pth=$1
if [ -d "${pth}" ] 
	then
	ls -1F $pth>usbdata.txt
	echo "dir files are written"
else
 	if [ -f "${pth}" ] 
	then 
		cp $pth ./gcode/gcode.txt
		echo "file copied">usbdata.txt
		echo "file copied"
	else
		echo "file is not valid">usbdata.txt
		echo "file is not valid"
		exit 1
	fi
fi 
