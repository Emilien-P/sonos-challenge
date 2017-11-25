'use strict';

const assert = require('assert'),
    SonosConnector = require('../../javascripts/sonos/connector.js'),
    SonosGroupVolume = require('../../javascripts/sonos/groupVolume.js'),
    hhid = '<YOUR_HHID>',
    gid = '<YOUR_GROUPID>',
    url = 'ws://<YOUR_PLAYER_IP>:1400/websocket/api';

/*
 * Test application startup
 */

describe('Test the volume connection', function() {
    const connection = new SonosConnector();

    before(function(done) {
        connection.onConnected = function() {
            connection.volume = new SonosGroupVolume(connection);
            done();
        };

        // Need connection info here for a player or simulator
        connection.connect(hhid, gid, url);
    });

    it('receives getVolume response', function(done) {
        connection.volume.getVolume().then((response) => {
            console.log("getVolume response: " + JSON.stringify(response));
            done();
        }, (err) => {
            console.log("getVolume error: " + JSON.stringify(response));
            done(err);
        });
    });

    it('can setVolume', function(done) {
        connection.volume.setVolume(35).then((response) => {
            console.log("getVolume response: " + JSON.stringify(response));
            assert('header' in response);
            assert('success' in response.header);
            assert(response.header.success);
            done();
        }, (err) => {
            done(err);
        });
    });

    it('can getVolume', function(done) {
        connection.volume.getVolume().then((response) => {
            console.log("getVolume response: " + JSON.stringify(response));
            assert('header' in response);
            assert('success' in response.header);
            assert(response.header.success);
            assert('body' in response);
            assert('volume' in response.body);
            assert(response.body.volume === 35);
            done();
        }, (err) => {
            done(err);
        });
    });

    after(function() {
        connection.disconnect();
    });
});
