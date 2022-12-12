import { 
    getEmailLogsList,
    resend,
 } from '../cen/static/js/index.js';


describe('getEmailLogsList', () => {
    beforeEach(() => {
        global.fetch = jest.fn();
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

describe('resend', () => {
    const id = 123;
    beforeEach(() => {
        global.$ = jest.fn();
        global.$.mockReturnValue({
            html: () => id
        });
        global.fetch = jest.fn();
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')}));
    });
   it('should call fetch with correct url', async () => {
       await resend();
       expect(global.fetch).toHaveBeenCalledWith(`/api/tasks/${id}/resend`, { method: 'POST', });
    });
});