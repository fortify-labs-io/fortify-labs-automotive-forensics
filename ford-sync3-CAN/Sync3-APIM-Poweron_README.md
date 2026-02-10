# Ford SYNC APIM Bench Power-On Procedure

Simple guide for powering on Ford SYNC APIM units on the bench for testing and analysis.

## Procedure to Power on Unit

Visit our [Fortify Labs Automotive Forensics Github repository - Ford Sync CAN](https://github.com/fortify-labs-io/fortify-labs-automotive-forensics/tree/main/ford-sync3-CAN) 

1. Connect Infotainment Unit to Power Supply Pins as follows:

   |Function|Pin|
   |-|-|
   |Power|1|
   |Ground|37|
   |CAN High|19|
   |CAN Low|20|

   >Note: Ensure power supply is capable of supplying 5 Amps.

2. Initialize CAN Interface:

   ```bash
   sudo ip link set can0 type can bitrate 500000
   sudo ip link set can0 up
   ```

3. Save the following CAN message log to a log file and play it with `canplayer`:

   - CAN messages to be played:

     ```
     (1770336540.380455) can0 30A#C700000000000000
     (1770336540.380701) can0 318#00000000000AAE00
     (1770336540.380845) can0 346#000000030300C000
     (1770336540.381595) can0 348#0000000000000000
     (1770336540.391619) can0 303#000008060E052000
     (1770336540.391870) can0 307#0600000000000000
     (1770336540.392120) can0 38A#4000400100470000
     (1770336540.392345) can0 3B3#1080000CFE000000
     (1770336540.392595) can0 3CA#2E80000000000000
     (1770336540.392845) can0 3D0#034F000088000F89
     (1770336540.413723) can0 3B4#401111FF1E1E0000
     (1770336540.417698) can0 3CA#2E80000000000000
     (1770336540.423056) can0 3B5#00D700D500E600E8
     (1770336540.445371) can0 3E8#4088000000000000
     (1770336540.448496) can0 3CA#2E80000000000000
     (1770336540.462985) can0 3B2#1080C00CE6000002
     (1770336540.465743) can0 3C3#400C000000008000
     (1770336540.477715) can0 3CA#2E80000000000000
     (1770336540.480122) can0 318#00000000000AAE00
     (1770336540.480371) can0 346#000000030300C000
     (1770336540.480622) can0 348#0000000000000000
     ```

   - Using `canplayer` to start the system:

     ```bash
     canplayer -I poweron.log
     ```

4. The head unit should now be powered on.

## Author

Created for automotive cybersecurity research and reverse engineering analysis.

## License

This tool is provided for legitimate automotive security research and forensic analysis purposes.

**Disclaimer:** This information is for educational and research purposes only. Working with automotive control systems can affect vehicle safety systems. Only perform these procedures on bench setups, not in vehicles. The author assumes no liability for misuse or damage.
