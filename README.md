# BlueControlv1.0 is licensed under <a href= 'https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1)'>CC BY-NC-SA 4.0</a> (<a href= 'https://www.linkedin.com/posts/srikanthsugavanam_github-srikanths-iitbluecontrol-ee536-activity-7117839407281270785-Yqxn?utm_source=share&utm_medium=member_desktop)'>Open-Source @IIT Mandi</a>)
[EE536: Internet of Things] BlueControl : Instrument Automation with SCPI over Bluetooth

For now I have worked with two Instruments:
1. DSOX1102A KeySight Technologies (Digital Storage Oscilloscope)
2. AFG1062 Tektronix (Arbitrary Function Generator) 

Python modules used:
1. pyserial or pyusb
2. pyvisa (for sending SCPI commands to instruments)
3. pybluez (bluetooth library)
4. zeroconf (instrument discovery and service registration) - Without this, the code generates a warning.

Architecture:

![image](https://github.com/SKundawal/BlueControl/assets/61798659/f9c1187a-2393-46a0-9c0e-e9040619d1ac)

Future Scope:
1. Few scpi commands are not working (trying to figure out why...)
2. Store output from query commands in a file.
3. SCPI commands can be given using a file with input values.
4. Make a proper desktop application for the same.
