# Steam Account Switcher Manager `1.0`

![Static Badge](https://img.shields.io/badge/OS-Windows_Only-blue)

SASM is a powerful tool designed to enhance the management of your Steam accounts. With the Steam's limitation of displaying only five accounts at a time, SASM allows you to reorder accounts, temporarily hide them, and more.

<img src="https://github.com/user-attachments/assets/0abf826c-cc89-477e-82d3-8ed52dc3b96a" alt="GUI Preview" width="500" />

## Features

- **Account Management**: Easily reorder your Steam accounts to suit your preferences.
- **Temporary Hiding**: Hide accounts temporarily to declutter your view.
- **Account Disabling**: Disable accounts for privacy or organization, with hidden accounts stored in `%appdata%/KRWCLASSIC/steamaccountswitchermanager`.

## Installation

1. Download `main.pyw` and `requirements.txt` files.
2. Install the required packages by running:

   ```cmd
   pip install -r requirements.txt
   ```

3. Run `main.pyw` file

> You can also build this project with Nuitka or PyInstaller if you prefer binaries.

## Usage

- Launch the application to view your accounts.
- Use the interface to reorder or hide accounts as needed.
- Access the settings to manage account via right click.

## Fun Additions

- Made name fields editable so you can temporarily change account name(s) in Steam's account switcher.

## TODO

- Backup system
- Auto editing so your changes are permanent (might break adding new accounts - to remember)

## Thanks

To Rossen Georgiev for developing the "vdf" package.

## Support

For any issues or feature requests, please open an issue on the GitHub repository.
