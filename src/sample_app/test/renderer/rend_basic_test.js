'use strict';

const assert = require('assert'),
    mocha = require('mocha');

describe('Smoke Test', function() {
    it('starts up without crashing', function() {
        assert.strictEqual(window.mocha, mocha);
    });

    it('loaded the UI but the not the DOM', function() {
        const name = document.body.firstElementChild.nodeName;
        console.log('Name is ' + name);
        assert.ok(name !== null);

        // This shows that the DOM is not being loaded from the Electron Application
        const coverdiv = document.getElementById('cover-art');
        assert.ok(coverdiv === null);
    });
});
