Ege modifications:
	views/index.html (added button for testing a session creation)
	views/index.js (read first part for modifs and current errors)
	stylesheets/style.css (button img for testing)

_______________________________________

Sonos Javascript Control API Sample App
=======================================

The Sonos Javascript Control API sample app is an application written in the Electron application framework.
This sample application searches and finds Sonos players and groups on the local network, allows users to
connect and control a groups playback and volume while displaying album art and metadata.

## Supported Platforms

Currently working on Apple Mac OSX and Microsoft Windows.

## Prerequisites

- NodeJS runtime environment
- NPM, Node Package Manager

## Install the app

Download and copy the tar.gz package into a directory and then run the following:

On Mac copy the file to a directory and unpack the tar.gz file.

```sh
tar xzvf sonos-js-control-api-sample-app-<VERSION>.tar.gz
```

On Windows use a reliable tool such as 7-zip to unpack the tar.gz file into a directory.

After you unpack the compressed archive file run `npm install` on the command line in the directory that contains
the package.json file.  This will install NodeJS extensions that are required by the sample app.

```sh
npm install
```

# Run the sample app

To run the Sonos Javascript Sample App, execute the following command in the directory where it is installed.

```sh
npm start
```
To stop the app, type CTRL-C or close your console window.
On mac command-Q also works to quit the application.

The app outputs messages to the console.

# Select A Group
Click **Select A Group** to display a list of groups in your network. Then click a group to control.


# Known Issues

* If another process is already listening on port 1900 when the Javascript Sample App starts, it may select a different port. In this case, the Javascript Sample App will not receive multicast advertisements from Sonos players (or the Sonos  simulator) but will still successfully discover them by sending searches when the group menu is opened. If a player or the simulator starts up while the app's group menu is open, it may not appear in the menu until the menu is closed and reopened.

# Read More

For more information and examples on how to discover, connect to and control a Sonos player using the Sonos Control API,
see the [Getting Started page](https://developer.sonos.com/control-api/getting-started) on the developer portal.

# Revision History

* Version 0.2: Initial Release
	- Changed WebSocket library to improve secure connection handling.
	- Improved volume slider code to better demonstrate optimizing event handling.
	- Fixed issue with not displaying the correct volume when muting players with the Sonos app.
	- Fixed issue so that the sample app disables controls when there is no content on the player.
* Version 0.1: Early Release

