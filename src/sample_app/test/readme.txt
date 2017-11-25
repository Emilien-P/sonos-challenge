# Javascript Sample App Testing 

## Application Structure

This sample is an Electron application and runs as two processes referred to as main and renderer. The main process is an instance of nodeJS running native to the machine so it has access to the network stack and local files. The renderer process is an instance of the Chromium browser and is used for user interface display.

## Automated Testing
Since the application is built in two parts there are two directories in the test folder.  One for the main process tests and one for the renderer process tests.  To run the main tests from the root directory of the app type:
> npm test

To run the renderer tests type:
> npm run-script testr

*NOTE: There is an issue in the test framework and the Chromium browser does not launch for renderer tests.*

## Hand Testing

To run the app and test you can start it with:
> npm start

To open the javascript console and browse the DOM of the app you can open the Developer Tools from the View menu.
