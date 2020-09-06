# <img src="https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/print.svg" card_color="#FEE255" width="50" height="50" style="vertical-align:bottom"/> skill-print

## About
Mycroft skill to support output on receipt thermo printer.

Only tested with a cheap thermo receipt printer that has 'PT-210' as the only marking on the device...

In theory this should work with every printer that is connected via USB and accepts plaintext (ESC/POS) commands.

## Configuration
This skill will only work on a custom mycroft instance such as picroft on a Raspberry Pi.

Before the skill can be used, the user who runs picroft has to be added to the 'lp' (line printer) system group.

Example that works in most cases.

```
sudo addgroup pi lp
```

Now, attach the printer to the USB port.

In the ideal case, the printer shows under ```/dev/usb/lp0```.

```
$ file /dev/usb/lp0
/dev/usb/lp0: character special (180/0)
```
Add this path to the 'local path' setting on the Mycroft skills config page.

In some rare cases, it might be required to add a new udev role to the system.

Please consult the internet about this...


### Skill Settings
Access the skill settings via Mycroft Skills page.
- [mycroft.ai](https://account.mycroft.ai/skills)

The following configuration options exist for this skill.

- Printer is connected (check this if you believe that your printer is ready and you want to use it.)
- Prints out everything Mycroft says when checked. (Does exactly that...)
- Print current date/time with message (Prints date/time before it prints the message.)
- Add a line feed after each message (Does exaclty that...)
- Message buffer (Allows you to maintain a message buffer of any size that can be accessed and printed.)



## Example voice commands
* "Enable printer"
* "Disable printer"
* "Enable linefeed"
* "Disable linefeed"
* "print time"
* "print buffer"
* "..."

## Installation
### Manual
To manually install the skill, go to the Mycroft core directory and run the below.

```mycroft-msm install https://github.com/tobus3000/skill-print.git```

## Credits
tobus3000

## Category
**Information**

## Tags
#Print
