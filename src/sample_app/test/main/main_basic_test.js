'use strict';

const assert = require('assert');

/*
 * Test application startup
 */

describe('Initialization', function() {
    it('Starts without errors', function() {
        // TODO Check for valid application initialization here
        assert(true);
    });
});

describe('Group manager', function() {
    const GroupManager = require('../../javascripts/sonos/groupManager').getInstance();
    it('refreshes groups without errors', function() {
        GroupManager.refreshGroups();
    });

    it('has a list of players', function(done) {
        setTimeout(function() {
            const groups = GroupManager.groups();
            console.log('Number of groups ' + groups.length);
            assert(groups.length > 0);
            done();
        }, 500);
    });
});
