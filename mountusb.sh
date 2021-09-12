p=`fdisk -l | tail -2 | grep -oP '.{0,8}sd.{0,3}'`
echo $p
mount -t vfat -o rw $p /media/usbstick
ls /media/usbstick>usbdata.txt
