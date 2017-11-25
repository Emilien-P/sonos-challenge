'use strict';

/*
 The MIT License (MIT)

 Copyright (c) 2015 Sonos, Inc.

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 */

const fs = require('fs'),
    tls = require('tls');

// Needed for running the tests outside of chromium
if (typeof WebSocket === 'undefined') {
    var WebSocket = require('websocket').client;
}

/**
 * The SonosConnector wraps the WebSocket connection to the group coordinator of a Sonos group, and handles sending
 * Control API commands, transmitting Control API events to the app, etc.
 * @constructor
 */
function SonosConnector() {
    /**
     * Holds the trusted Sonos root CA certificates, used for checking player certificates when using secure WebSocket
     * connections
     * @private
     */
    this._sonosCAs = [];

    this.householdId = '';
    this.groupId = '';
    this.apiKey = '1e31c6cf-0834-41df-8795-5f9ce11a0164';
    this.subProtocol = 'v1.api.smartspeaker.audio';
    this.websocket = null;
    this.listeners = {};
    this.cmdResolveHandlers = {}; // map of cmdId to resolve handlers
    this.cmdRejectHandlers = {}; // map of cmdId to reject handlers
    this.cmdIdCounter = 0;

    console.log('Loading trusted Sonos root CAs...');
    this._sonosCAs.push(fs.readFileSync('https/sonos-current-device-root.pem'));
    this._sonosCAs.push(fs.readFileSync('https/sonos-future-device-root.pem'));
    console.log('Loaded ' + this._sonosCAs.length + ' Sonos root CAs');
}

/**
 * Surfaces errors to the user via an alert dialog if available (i.e. running in a Chromium window), otherwise
 * via the console log. Also terminates the WebSocket connection.
 * @param {SonosConnector} connector the {@link SonosConnector} that owns this WebSocket
 * @param {Error} error the error to display to the user
 */
function onError(connector, error) {
    if (typeof alert === 'function') {
        alert('Error: ' + JSON.stringify(error));
    } else {
        console.log('Error: ' + JSON.stringify(error));
    }

    if (connector.websocket) {
        connector.websocket.close();
    }
}

/**
 * Called when the WebSocket is successfully opened.
 * @param {SonosConnector} connector the {@link SonosConnector} that owns this WebSocket
 */
function onOpen(connector) {
    if (typeof connector.onConnected === 'function') {
        connector.onConnected();
    }
}

/**
 * Called when the WebSocket is closed.
 * @param {SonosConnector} connector the {@link SonosConnector} that owns this WebSocket
 */
function onClose(connector) {
    if (typeof connector.onDisconnected === 'function') {
        connector.onDisconnected();
    }
}

/**
 * Handles incoming messages from the WebSocket connection (i.e. Control API events and command responses).
 * @param {SonosConnector} connector the {@link SonosConnector} that owns this WebSocket
 * @param {string} message a stringified JSON Control API message
 */
function onMessage(connector, message) {
    const msg = JSON.parse(message.utf8Data),
        header = msg[0],
        body = msg[1],
        msgObj = {
            header: header,
            body: body
        },
        response = ('response' in header) ? header.response : undefined;

    if (response) {
        // responses are handled separately from events
        const cmdId = ('cmdId' in header) ? header.cmdId : undefined,
            success = ('success' in header) ? header.success : false;

        // call the promise resolve or reject handlers if present
        if (cmdId) {
            if (connector.cmdResolveHandlers[cmdId] && connector.cmdRejectHandlers[cmdId]) {
                if (success) {
                    connector.cmdResolveHandlers[cmdId](msgObj);
                } else {
                    connector.cmdRejectHandlers[cmdId](msgObj);
                }
                delete connector.cmdResolveHandlers[cmdId];
                delete connector.cmdRejectHandlers[cmdId];
            }
        }

    } else if (typeof connector.listeners[header.namespace] === 'function') {
        connector.listeners[header.namespace](msgObj);
    }
}

/**
 * Attempts to connect to a Sonos group coordinator via WebSocket at the given address.
 * @param {string} hid the ID of the Sonos Household to which the target group belongs
 * @param {string} gid the Group ID of the target Sonos group
 * @param {string} url the WebSocket endpoint address of the Sonos group's coordinator; if this is a wss:// address,
 *                     connect via secure WebSocket over HTTPS
 */
SonosConnector.prototype.connect = function(hid, gid, url) {
    this.householdId = hid;
    this.groupId = gid;

    const self = this,
        socketUrl = url + '?key=' + this.apiKey,
        options = {
            ca: this._sonosCAs,
            rejectUnauthorized: false
        },
        urlObj = require('url').parse(url);
    try {
        self.websocket = new WebSocket({
            tlsOptions: {
                ca: this._sonosCAs,
                rejectUnauthorized: true,
                checkServerIdentity: () => {
                    return undefined;
                }
            }
        });
        self.websocket.on('connectFailed', error => {
            onError(self, error);
        });

        self.websocket.on('connect', connection => {
            connection.on('error', error => {
                onError(self, error);
            });
            connection.on('close', () => {
                self.send = undefined;
                self.closeWebsocketConnection = undefined;
                onClose(self);
            });
            connection.on('message', message => {
                onMessage(self, message);
            });

            self.send = message => {
                connection.send(message);
            };

            self.closeWebsocketConnection = () => {
                connection.close();
            };

            onOpen(self);
        });

        self.websocket.connect(socketUrl, [self.subProtocol]);
    } catch (err) {
        onError(self, err);
    }
};

/**
 * Disconnects from the current Sonos group.
 */
SonosConnector.prototype.disconnect = function() {
    this.householdId = '';
    this.groupId = '';
    this.listeners = {};
    if (typeof this.closeWebsocketConnection === 'function') {
        this.closeWebsocketConnection();
    }
};

/**
 * Registers listeners for different namespace messages.
 * @param {string} namespace the Control API namespace to subscribe to
 * @param {function} callback a function to handle incoming Control API events
 */
SonosConnector.prototype.listen = function(namespace, callback) {
    this.listeners[namespace] = callback;
};

/**
 * Creates and returns a new cmdId string to be used to send a Control API command.
 * @returns {string} a new cmdId string.
 */
SonosConnector.prototype.createCmdId = function() {
    const cmdId = (this.cmdIdCounter == Number.MAX_VALUE) ? 0 : (this.cmdIdCounter + 1);
    return cmdId.toString();
};

module.exports = SonosConnector;
