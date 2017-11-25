'use strict';

// added playbackSession
// added new button (check html file) to test {createSession}
// createSession is successful, but need to receive sessionId
// then with sessionId, can {loadCloudQueue}
// for the cloud queue app, I used the template that sonos has given with a redirection to a local library of tracks

// problems:
// - oauth dance for the simple model
// - how to setup the sessionId
// - loading the queue to the player

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


const SonosConnector = require('../javascripts/sonos/connector.js'),
    SonosGlobal = require('../javascripts/sonos/global.js'),
    SonosGroupVolume = require('../javascripts/sonos/groupVolume.js'),
    SonosPlayback = require('../javascripts/sonos/playback.js'),
    SonosPlaybackMetadata = require('../javascripts/sonos/playbackMetadata.js'),
    // added playback session to create a session with a sonos player.
    SonosPlaybackSession = require('../javascripts/sonos/playbackSession.js'),
    ipcRenderer = require('electron').ipcRenderer, // Communication to the server
    connection = new SonosConnector(); // SonosConnector manages the connection to a Sonos group

let isDraggingVolume = false,
    currentVolume = 0,
    hasCreatedSession = false;

/**
 * This function executes after the connection to the Sonos Player has succeeded
 * and wires the page to the SonosConnector object.
 */
connection.onConnected = function onConnected() {

    // Create the control objects for the new connection
    connection.session = new SonosPlaybackSession(connection);   // playback session to play from cloud queue
    connection.volume = new SonosGroupVolume(connection);        // Sends volume command and receives volume events
    connection.playback = new SonosPlayback(connection);         // control playback and receive playback events
    connection.metadata = new SonosPlaybackMetadata(connection); // Receives now playing/up next metadata information
    connection.global = new SonosGlobal(connection);             // Receives global notification messages

    // Setting the event callbacks on the Sonos Control Objects once the connection is complete

    connection.volume.subscribe(function(msg) {
        if (msg.header.type === 'groupVolume') {

            const $volumeSlider = $('#volume');

            // If event says fixed volume then disable controls and don't expect any more messages
            $volumeSlider.toggleClass('fixed', msg.body.fixed);

            // Cache last evented volume from the group
            currentVolume = msg.body.muted ? 0 : msg.body.volume;

            // Ignore the volume update events when dragging
            if (!isDraggingVolume) {
                const $dataSlider = $('[data-slider]');
                if ($dataSlider.hasClass('settling')) {
                    $dataSlider.data('settle-value', currentVolume);
                } else {
                    $dataSlider.data('slider-object').setValue(currentVolume);
                }
            }
        }
    });

    connection.playback.subscribe(function(msg) {
        if (msg.header.type === 'playbackStatus') {
            console.log('playback status message.');
            const isPlaying = ['PLAYBACK_STATE_PLAYING', 'PLAYBACK_STATE_BUFFERING']
                    .indexOf(msg.body.playbackState) > -1;
            $('#play-controls').find('.play').toggleClass('playing', isPlaying);
        }
    });

    connection.metadata.subscribe(function(msg) {
        if (msg.header.type === 'metadataStatus') {
            const $controlButtons = $('#play-controls').find('.control.button');
            if (!msg.body.hasOwnProperty('currentItem') && !msg.body.hasOwnProperty('nextItem')) {
                $controlButtons.addClass('disabled');
            } else {
                $controlButtons.removeClass('disabled');
            }

            try {
                $('.current.song').html(msg.body.currentItem.track.name);
                $('.current.artist').html(msg.body.currentItem.track.artist.name);
                $('#cover-art').attr('src', msg.body.currentItem.track.imageUrl).show();
            } catch (err) {
                $('div.current').html('');
                $('#cover-art').hide();
                console.log('No metadata for current item');
            }

            try {
                $('div.nextup.song').html(msg.body.nextItem.track.name);
                $('div.nextup.artist').html(msg.body.nextItem.track.artist.name);
                $('#nextup-title').show();
            } catch (err) {
                $('#nextup-title').hide();
                $('div.nextup').html('');
                console.log('No metadata for next item');
            }
        }
    });

    connection.global.subscribe(function(msg) {
        if (msg.header.type === 'groupCoordinatorChanged') {
            const $groupName = $('#group-name');
            switch (msg.body.groupStatus) {
                case 'GROUP_STATUS_UPDATED':
                    $groupName.html(msg.body.groupName);
                    break;
                case 'GROUP_STATUS_GONE':
                    lostControlOfSonos();
                    break;
                case 'GROUP_STATUS_MOVED':
                    disconnect();
                    $groupName.html(msg.body.groupName);
                    connection.connect(msg.header.householdId, msg.header.groupId, msg.body.websocketUrl);
                    break;
            }
        }
    });

    $('#control-content').removeClass('disconnected');
};

/**
 * Set the enabled or disabled state of the volume slider.
 * NYI.
 * @param {boolean} enable
 */
function enableVolumeSlider(enable) {
}

/**
 * Handles loss of control of the current Sonos group
 */
function lostControlOfSonos() {
    $('#group-name').html('Select A Group');
    $('#cover-art, #nextup-title').hide();
    disconnect();
    alert("Lost control of Sonos!");
}

/**
 * Disconnect from the Sonos player.
 */
function disconnect() {
    const $playControls = $('#play-controls');
    $playControls.find('.play').removeClass('playing');
    $playControls.find('.control.button').removeClass('disabled'); // don't stack disabled with disconnected

    $('div.song, div.artist').html('');
    $('#control-content').addClass('disconnected');
    connection.disconnect();
}

/**
 * Build the UI elements for the group list.
 * @param {Object[]} list the discovered groups
 * @param {string} list[].householdId the Sonos household ID of the discovered group
 * @param {string} list[].groupId the group ID of the discovered group
 * @param {string} list[].groupName the display name of the discovered group
 * @param {string} list[].address the WebSocket URI of the group coordinator
 */
function buildGroupList(list) {
    const $groupList = $('#group-list'),
        curGroupId = connection.groupId;
    let isCurGroupMissing = (curGroupId && curGroupId.length > 0);
    $groupList.html('');
    list.forEach(function(g) {
        const d = document.createElement('div');
        $(d).addClass('group-item')
            .html(g.groupName)
            .appendTo($groupList)
            .click(function() {
                disconnect();
                connection.connect(g.householdId, g.groupId, g.address);
                $('#group-name').html(g.groupName);
                $groupList.slideUp();
            });
        if (curGroupId === g.groupId) {
            isCurGroupMissing = false;
        }
    });
    if (isCurGroupMissing) {
        lostControlOfSonos();
    }
}

// When the page is ready then setup the group connection control
$(document).ready(function() {
    const $dataSlider = $('[data-slider]'),
        $playControls = $('#play-controls'),
        bufferMillis = 200;
    let lastChangeTime = Date.now();

    // Handle group events from the main service that contain a list of all available players
    ipcRenderer.on('GroupManager:groups', function(event, data) {
        buildGroupList(data);
    });

    // On click slide open/close group list and initiate another search for players
    $('#group-name').on('click', function() {
        $('#group-list').slideToggle();
        ipcRenderer.send('GroupManager:getGroups');
    });

    // additional button, initiate a session with a player
    // check out index.html
    // --> get response --> sessionId necessary for loading the cloud queue
    $playControls.find('.session').on('click', function(event){
      var response = connection.session.createSession('abc', 'ctxt', 'data');

      var fs = require('fs');
      fs.writeFile("/Users/ege/Desktop/myf.txt", `${response.header.namespace}` , function(err) {
          if(err) {
              return console.log(err);
          }

          console.log("saved");
      });

      var sessionId = responseObj[1].sessionId;
      console.log(sessionId);

      // testing the cloudqueue Loading: (error need sessionId)
      connection.session.loadCloudQueue('http://localhost:3000');
    });

    $playControls.find('.play').on('click', function(event) {
        if (connection.playback && !$(this).hasClass('disabled')) {
            const isPlaying = $(event.target).hasClass('playing');
            if (isPlaying) {
                connection.playback.pause();
            } else {
                connection.playback.play();
            }

            $(event.target).toggleClass('playing', !isPlaying);
        }
    });

    $playControls.find('.previous, .next').on('click', function() {
        if (connection.playback && !$(this).hasClass('disabled')) {
            if ($(event.target).hasClass('previous')) {
                connection.playback.skipToPreviousTrack();
            } else {
                connection.playback.skipToNextTrack();
            }
        }
    });

    $dataSlider.on('slider:changed', function(event, data) {
        const now = Date.now(),
            v = Math.round(data.value);

        // Only send a setVolume command if slider value is different from the last event we saw from the group, and
        // it's been at least 200ms since the we sent the last command.
        if (connection.volume && now - lastChangeTime >= bufferMillis && v !== currentVolume) {
            lastChangeTime = now;
            connection.volume.setVolume(v);
        }
    });

    $dataSlider.on('slider:drag-started', function(event, data) {
        if (connection.volume) {
            isDraggingVolume = true;
        }
    });

    $dataSlider.on('slider:drag-ended', function(event, data) {
        if (connection.volume) {
            connection.volume.setVolume(Math.round(data.value));
            if (isDraggingVolume) {
                isDraggingVolume = false;
                const $dataSlider = $('[data-slider]');
                $dataSlider.data('settle-value', data.value);
                $dataSlider.addClass('settling');
                setTimeout(function() {
                    // Make sure we did not start dragging again right away
                    if (!isDraggingVolume) {
                        $dataSlider.data('slider-object').setValue($('[data-slider]').data('settle-value'));
                    }

                    $dataSlider.removeClass('settling');
                }, 200);
            }
        }
    });
});
