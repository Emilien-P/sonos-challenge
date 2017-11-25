'use strict';

/*
 The MIT License (MIT)

 Copyright (c) 2016 Sonos, Inc.

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


// Code generated on 2016-05-03 08:31:31.561887. *** DO NOT MODIFY ***

/**
 * @param {SonosConnector} connector the {@link SonosConnector} for the current connection
 * @constructor
 */
function SonosPlaybackSession(connector) {
    this.namespace = 'playbackSession:1';
    this.connector = connector;
}

/**
 * Send a Sonos Control API command in this namespace to the Sonos player
 * @param {string} command the name of the command
 * @param {Object} body the command parameters, or an empty object if omitted
 * @returns {Promise} a promise that will be fulfilled if the command is successful, rejected if it fails
 */
SonosPlaybackSession.prototype.command = function(command, body) {
    const namespace = this.namespace,
        connector = this.connector;
    return new Promise(function(resolve, reject) {
        const cmdId = connector.createCmdId();
        if (body === undefined) {
            body = {};
        }
        const header = {
            namespace: namespace,
            householdId: connector.householdId,
            groupId: connector.groupId,
            cmdId: cmdId,
            command: command
        };
        connector.cmdResolveHandlers[cmdId] = resolve;
        connector.cmdRejectHandlers[cmdId] = reject;
        connector.send(JSON.stringify([header, body]));
    });
};

SonosPlaybackSession.prototype.subscribe = function(callback) {
    this.connector.listen(this.namespace, callback);
    return this.command('subscribe');
};

SonosPlaybackSession.prototype.unsubscribe = function() {
    this.connector.listen(this.namespace);
    return this.command('unsubscribe');
};

SonosPlaybackSession.prototype.joinOrCreateSession = function(appId, appContext, customData) {
    return this.command('joinOrCreateSession', {
        'appId': appId,
        'appContext': appContext,
        'customData': customData
    });
};

SonosPlaybackSession.prototype.joinSession = function(appId, appContext) {
    return this.command('joinSession', {
        'appId': appId,
        'appContext': appContext
    });
};

SonosPlaybackSession.prototype.createSession = function(appId, appContext, customData) {
    return this.command('createSession', {
        'appId': appId,
        'appContext': appContext,
        'customData': customData
    });
};

SonosPlaybackSession.prototype.leaveSession = function() {
    return this.command('leaveSession');
};

SonosPlaybackSession.prototype.loadCloudQueue = function(queueBaseUrl, httpAuthorization, itemId, positionMillis, playOnCompletion, trackMetadata) {
    return this.command('loadCloudQueue', {
        'queueBaseUrl': queueBaseUrl,
        'httpAuthorization': httpAuthorization,
        'itemId': itemId,
        'positionMillis': positionMillis,
        'playOnCompletion': playOnCompletion,
        'trackMetadata': trackMetadata
    });
};

SonosPlaybackSession.prototype.refreshCloudQueue = function() {
    return this.command('refreshCloudQueue');
};

SonosPlaybackSession.prototype.skipToItem = function(itemId, queueVersion, positionMillis, playOnCompletion, trackMetadata) {
    return this.command('skipToItem', {
        'itemId': itemId,
        'queueVersion': queueVersion,
        'positionMillis': positionMillis,
        'playOnCompletion': playOnCompletion,
        'trackMetadata': trackMetadata
    });
};

SonosPlaybackSession.prototype.seek = function(itemId, positionMillis) {
    return this.command('seek', {
        'itemId': itemId,
        'positionMillis': positionMillis
    });
};

module.exports = SonosPlaybackSession;
