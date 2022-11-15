import $ from 'jquery';
import createApp from './cen/static/js/toolkit.js';

global.fetch = jest.fn(() => Promise.resolve({
    json: () => Promise.resolve({}),
}));

global.$ = $;

jest.mock('./cen/static/js/toolkit.js');
createApp.mockReturnValue({listen: jest.fn()});