import { getEmailLogsList } from '../cen/static/js/delivery.js';


describe('getEmailLogsList', () => {
    beforeEach(() => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')}));
    });
   it.each([
    ['limitValue', 'offsetValue', 'searchValue'],
    ['limitValue', 'offsetValue', undefined],
    ['limitValue', 'offsetValue', ''],
   ])('should call fetch with correct url', async (limitValue, offsetValue, searchValue) => {
        await getEmailLogsList(limitValue, offsetValue, searchValue);
        expect(global.fetch).toHaveBeenCalledWith(`/api/email_tasks?search=${searchValue}&limit=${limitValue}&offset=${offsetValue}`);
    });
});