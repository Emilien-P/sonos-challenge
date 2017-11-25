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

module.export = true;

/**
 * Find the index of a given value in an array.
 * @param {function} predicate the test to use on array elements
 * @param {*} thisValue used as the 'this' reference for predicate
 * @returns {number} the index of the first element for which predicate returns true, or -1
 */
Array.prototype.findIndex = function(predicate, thisValue) {
    const arr = Object(this);
    if (typeof predicate !== 'function') {
        throw new TypeError();
    }

    for (let i = 0; i < arr.length; i++) {
        if (i in arr) {  // skip holes
            const elem = arr[i];
            if (predicate.call(thisValue, elem, i, arr)) {
                return i;
            }
        }
    }

    return -1;
};

/**
 * Return an array element matching some criteria.
 * @param {function} predicate the test to use on array elements
 * @param {*} thisValue used as the 'this' reference for predicate
 * @returns {*|undefined} the first array element for which predicate returns true, or undefined
 */
Array.prototype.find = function(predicate, thisValue) {
    const i = this.findIndex(predicate, thisValue);
    return i === -1 ? undefined : this[i];
};

/**
 * Shuffle the array in-place using the Fisher-Yates algorithm.
 */
Array.prototype.shuffle = function shuffle() {
    let i,
        j,
        temp;

    for (i = this.length - 1; i > 0; i -= 1) {
        j = Math.floor(Math.random() * (i + 1));
        temp = this[i];
        this[i] = this[j];
        this[j] = temp;
    }
};
