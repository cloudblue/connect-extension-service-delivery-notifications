import {getSettings, getRules } from '../cen/static/js/settings.js';

global.fetch.mockReturnValue(Promise.resolve({
    json: () => Promise.resolve({email_sender: 'test@example.email', name: 'Test'}),
}));

let settings;

describe('getSettings', () => {
    beforeEach(async () => {
        settings = await getSettings();
    });
    it('should return settings', () => {
        expect(settings).toBeDefined();
    });
    it('should return email_sender', () => {
        expect(settings.email_sender).toBe('test@example.email');
    });
    it('should return name', () => {
        expect(settings.name).toBe('Test');
    });
});

describe('getRules', () => {
    it('should return rules', async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')}));
        const rules = await getRules();
        expect(rules).toBe('OK');
    });
});