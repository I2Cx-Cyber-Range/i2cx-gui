# I²Cx Graphical User Interface
Code source is available on GitHub
https://github.com/I2Cx-Cyber-Range/i2cx-gui

## I²Cx Scanner Lite
Port A => can drive 4 mA (needed for SWD)

Port B => can drive 16 mA (useful to force logic level on bus like I2C and SPI and avoid reset master)

### Install I²Cx Cyber Range graphical user interface
```console
pip3 install i2cx
```

### To start Graphical Interface of I²Cx Cyber Range
```console
i2cx
```

## I²Cx Cyber range can be used with OpenOCD (destination path need to adapted)
To use I²Cx Scanner Lite with openOCD you need to add a config file (available in tools folder) 
```console
wget https://github.com/I2Cx-Cyber-Range/i2cx-gui/tools/ftdi/conf_i2cx_scanner_-lite_lootus_pid.xml  -P /usr/local/share/openocd/scripts/interface/i2cx-scanner-lite.cfg
```

```console
openocd -f interface/i2cx-scanner-lite.cfg -f target/stm32f7x.cfg  -c "adapter speed 4000"
```

In another console
```console
telnet 127.0.0.1 4444
```

To read firmware
```console
flash read_bank 0 firmware.bin
```

# On Ubuntu 20.04

## Allow I2Cx Scanner Lite to non root user and Load FTDI driver to I2CX Scanner Lite
```console
wget https://github.com/I2Cx-Cyber-Range/i2cx-gui/tools/openocd/i2cx-scanner-lite.cfg -P /etc/udev/rules.d/35-i2cx-cyber-range.rules
```

or add manually both line to a new file for example: /etc/udev/rules.d/35-i2cx-cyber-range.rules

SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6E50", GROUP="plugdev"

ACTION=="add", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6e50", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c 'echo 0403 6e50 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'"

## In case of OpenGl issue
ImportError: libOpenGL.so.0: cannot open shared object file: No such file or directory
sudo apt update
sudo apt upgrade
sudo apt dist-upgrade
sudo apt-get install -y libopengl0

# I2CX on windows
The probably easiest way to deal with libusb on Windows is to use Zadig

Start up the Zadig utility

Select Options/List All Devices, then select the FTDI devices you want to communicate with. Its names depends on your hardware, i.e. the name stored in the FTDI EEPROM.

With FTDI devices with multiple channels, such as FT2232 (2 channels) and FT4232 (4 channels), you must install the driver for the composite parent, not for the individual interfaces. If you install the driver for each interface, each interface will be presented as a unique FTDI device and you may have difficulties to select a specific FTDI device port once the installation is completed. To make the composite parents to appear in the device list, uncheck the Options/Ignore Hubs or Composite Parents menu item.

Be sure to select the parent device, i.e. the device name should not end with (Interface N), where N is the channel number.

for example Dual RS232-HS represents the composite parent, while Dual RS232-HS (Interface 0) represents a single channel of the FTDI device. Always select the former.

Select libusb-win32 (not WinUSB) in the driver list.

Click on Replace Driver