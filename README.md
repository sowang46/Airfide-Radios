# Airfide-Radios

!!! Do not redistribute this repo without written permission from UCSD [WCSN group](http://xyzhang.ucsd.edu)  


This repo contains necessary instructions and resources for running experiments with Airfied Sparrow+ 802.11ad radio.
 - Set up and connect AP and STA.
 - Collect per beam RSS traces.
 - Create/modify beams in a codebook. 
 - Add wmi function calls to the Python controller.
 - Firmware patching.

### Basic runs 

For a simple AP/STA test you need two Sparrow+ radios (one acting as the AP and the other as the STA) and a host PC.
Connect two radios' port 2 to the host PC's via a switch or router.
You may need to mannually assign the host's route or ethernet IP address in order to access the radios.
Make sure you can access both radios using `ssh root@<radio_ip_addr>`.  


Next run the AP/STA setup scripts in `script`.
You can either copy the scripts to the radios and run it locally or run `ssh root@<radio_ip_addr> 'bash -s' < ap.sh` on the host.
After running the setup scripts, reboot both AP and STA by running `sudo reboot; exit`  


After reboot, ssh into the STA radio and check the link.
The 802.11ad interface in the radios is typically named `wlan0`.
Check if the link is established using `iw wlan0 link`.  

![iw_link_output.png]()

If you see an output like this, it means you have successfully created a millimeter wave connection between the two radios!


### Collect per beam RSS traces

In 802.11ad radios, the AP periodically transmits a series reference signals with each beam in the codebook.
The STA evaluates the received signal strength of each beam and selects the strongest one for DL transmission.
By default, the per beam RSS values are inaccessible to applications. 
However, we can inject a piece of code to the firmware to copy the per beam RSS values to a memory address that is readable by applications (in our case the Python server).
See [this paper](https://sowang46.github.io/files/v2x.pdf) for more details.  


The patched firmware can be found here: `firmwares/STA/wil6210_sparrow_plus_v2x_client.fw`.
To collect per beam RSS, we need to replace the original firmware with the patched one and run the Python server on the radio.
We also need to run a client either host or radio to collect the per beam RSS values.
The firmware is located at `/lib/firmware/wil6210_sparrow_plus.fw`.
Overwrite this file with the patched firmware and reboot the 802.11ad interface by running `ifconfig wlan0 down` followed by `ifconfig wlan0 up`.
Next, copy the Python server named `wil6210_server-2.2.0` in `python_server/` to the radio and run `python wil6210_server-2.2.0 <port_number>`.
The Python server program shows the firmware patch version so you can check if you have successfully replaced the firmware.  


Now start up the client script by running `python get_per_beam_rss.py --server_ip <radio_ip> --server_port <port_number>`. You should be able to see the visualized per beam RSS values in real time!

### Modify codebooks

In Airfied radios, the antenna weight of each beam is stored in the codebook file located at `/lib/firmware/wil6210_sparrow_plus.brd`.
You can use `wil6210_brd_mod` in `codebooks/` To check or modify the antenna weight in a codebook.
For more usage, run `./wil6210_brd_mod --help` (note: it seems this binary only works in ubuntu OS).

### Python controller 

See [this repo](https://github.com/sowang46/wil6210-controller) to create you customized functions in the Python controller, build the controller for different platforms, and more.

### Firmware patching

See [this repo](https://github.com/sowang46/wil6210-firmware-patch.git) for firmware patching.

### Debug

 - The radio's disk space is very limited. Try to store large file to `\tmp`.
