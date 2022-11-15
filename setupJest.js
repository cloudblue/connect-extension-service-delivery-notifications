import $ from 'jquery';

global.fetch = jest.fn(() => Promise.resolve({
    json: () => Promise.resolve({}),
}));

global.$ = $;