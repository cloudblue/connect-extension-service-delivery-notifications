import $ from 'jquery';
import createApp from './cen/static/js/libs/toolkit.js';

global.document.getElementById = () => ({
    style: {display: false},
    addEventListener: jest.fn(),
});

global.fetch = jest.fn(() => Promise.resolve({
    json: () => Promise.resolve({}),
}));

global.$ = $;
global.jQuery = $;
global.$.prototype.DataTable = jest.fn();

jest.mock('./cen/static/js/libs/toolkit.js');
createApp.mockReturnValue(Promise.resolve({}));