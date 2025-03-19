# Steam Account Switcher Manager `1.3.1`

![Static Badge](https://img.shields.io/badge/OS-Windows-blue)
![Static Badge](https://img.shields.io/badge/OS-Linux-orange)

<sub>Linux support is limited! Currently in a working state.</sub>

SASM is a powerful tool designed to enhance the management of your Steam accounts. With the Steam's limitation of displaying only five accounts at a time, SASM allows you to reorder accounts, temporarily hide them, and more.

## Features

- **Account Management**: Easily reorder your Steam accounts to suit your preferences.
- **Account Disabling**: Disable accounts for privacy or organizational purposes. Disabled accounts are stored in either `%appdata%/KRWCLASSIC/steamaccountswitchermanager` or `~/.KRWCLASSIC/steamaccountswitchermanager`, depending on your operating system.
- **Backup Manager**: Automatically or manually create backups and restore them from one button.

## Preview

<img src="https://github.com/user-attachments/assets/cc8e6369-d8c9-4edf-a713-bae0bb3ebc0c" alt="GUI Preview" width="500" />

## Prerequisites (Non-build)

- Windows 10 or higher | Linux distro like Ubuntu 22 or higher
- Python 3.10 or higher (3.12+ Not Recommended)

## Installation (Non-build)

1. Download `sasm.pyw` and `requirements.txt` files.
2. Install the required packages by running:

   ```bash
   pip install -r requirements.txt
   ```

3. Run `sasm.pyw` file

> You can also build this project with Nuitka or PyInstaller if you prefer binaries.
> Prebuild binaries are available in the [releases section](https://github.com/KRWCLASSIC/SteamAccountSwitcherManager/releases).

## Building

All notes about building are available [here](https://github.com/KRWCLASSIC/Steam-Account-Switcher-Manager/blob/main/building_scripts/building_note.txt). In the same folder you can find build scripts for different building tools and operating systems.

> `build_all.bat` is a script that builds all versions in a queue under Windows. It requires WSL to be installed and configured beforehand, which includes having Python packages installed on both systems. For more details, refer to the building note mentioned above.

## Usage

- Launch the application to view your accounts.
- Use the interface to reorder or disable accounts as needed.
- Access the right click menu to manage account additional settings.

## Fun Additions

- Made name fields editable so you can temporarily change account name(s) in Steam's account switcher.

## TODO

- Auto editing so your changes are permanent (might break adding new accounts - to remember)

## Thanks

To Rossen Georgiev for developing the "vdf" package.

To Jessiey Sahana for backup icon over at [iconscout](https://iconscout.com/free-icon/data-backup-3351569_2797152)

## Support

For any issues or feature requests, please open an issue on the GitHub repository.
