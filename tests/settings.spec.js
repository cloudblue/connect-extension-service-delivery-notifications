import settingsPage from '../cen/static/js/settings.js';
import createApp from '../cen/static/js/toolkit.js';


jest.mock('../cen/static/js/toolkit.js');
createApp.mockReturnValue({});

global.fetch.mockReturnValue(Promise.resolve({
    json: () => Promise.resolve({email_sender: 'test@example.email', name: 'Test'}),
}));

let settings;

describe('getSettings', () => {
    beforeEach(async () => {
        settings = await settingsPage.getSettings();
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

describe('main', () => {
    beforeEach(async () => {
        jest
        .spyOn(settingsPage, 'getSettings')
        .mockImplementation(() => Promise.resolve({email_sender: '', name: ''}));
        jest
        .spyOn(global, '$').mockImplementation(() => ({ html: jest.fn() }));
        await settingsPage.main();
    });
    it('should call getSettings',  () => {
        expect(settingsPage.getSettings).toHaveBeenCalled();
    });
    it('should call $ with email_sender', () => {
        expect($).toHaveBeenCalledWith('#email_sender');
    });
    it('should call $ with name', () => {
        expect($).toHaveBeenCalledWith('#name');
    });
});