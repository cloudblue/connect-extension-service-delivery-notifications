import { getRules } from '../cen/static/js/index.js';


describe('getRules', () => {
    it('should return rules', async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')}));
        const rules = await getRules();
        expect(rules).toBe('OK');
    });
});