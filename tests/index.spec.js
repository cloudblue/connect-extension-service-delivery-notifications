import { 
    getEmailLogsList,
    main,
    showMailDetailModal,
    hideMailDetailModal,
    populateDataTable,
    toggleDisabledClassOnPageUp,
    toggleDisabledClassOnPageDown,
    createTable,
    getProductLogo,
    getVisibilityButton,
    resend,
    getDate,
 } from '../cen/static/js/index.js';

let expected;
let app;
const jquery = global.$;

describe('getEmailLogsList', () => {
    beforeEach(() => {
        jest.spyOn(global, 'fetch').mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')
        }));
        document.body.innerHTML = `
            <div id="loader-container"></div>
            <div id="settings"></div>
        `;
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

describe('main', () => {
    const getElementById = document.getElementById;
    beforeEach(() => {
        jest.spyOn(global, '$').mockReturnValue({
            DataTable: () => ({title: 'table'}),
            on: jest.fn()
        });
        app = {
            emit: jest.fn()
        };
        jest.spyOn(document, 'getElementById').mockReturnValue({
            addEventListener: jest.fn()
        });
        document.body.innerHTML = `
            <div id="mailDetailModal"></div>`;

        main(app);
    });

    afterEach(() => {
        // to clear mocks from beforeEach
        global.$ = jquery;
        document.getElementById = getElementById;
    });

    it('should add event listener show.mdb.modal', () => {
        expect(document.getElementById().addEventListener).toHaveBeenCalledWith('show.mdb.modal', expect.any(Function))
    });
    it('should add event listener hide.mdb.modal', () => {
        expect(document.getElementById().addEventListener).toHaveBeenCalledWith('hide.mdb.modal', expect.any(Function))
    });
    it('should emit size with height set to 800', () => {
        expect(app.emit).toHaveBeenCalledWith('$size', {"height": 800})
    });
});

describe('hideMailDetailModal', () => {
    let table;
    const draw = jest.fn()
    beforeEach(() => {
        app = {
            emit: jest.fn()
        };
        table = {
            page: () => ({
                draw
            })
        };

        hideMailDetailModal(app, table)();
    });

    it('should call table.page.draw', () => {
        expect(table.page().draw).toHaveBeenCalledWith('page')
    });

    it('should emit size with height set to 800', () => {
        expect(app.emit).toHaveBeenCalledWith('$size', {"height": 800})
    });
});

describe('showMailDetailModal', () => {
    const event = {
        relatedTarget: {
            getAttribute: () => 'recipient'
        }
    };
    const format = jest.fn();
    beforeEach(() => {
        jest.spyOn(global, '$').mockReturnValue({html: jest.fn()});
        jest.spyOn(global, 'fetch').mockReturnValue(Promise.resolve({
            json: () => Promise.resolve({
                email_from: 'email from',
                email_to: 'email to',
                product_id: 'product id',
                product_name: 'product name',
                asset_id: 'asset id',
                request_id: 'request id',
                body: 'email body'
            })
        }));
        app = {
            emit: jest.fn()
        };
        global.moment = {
            utc: () => ({
                format
            })
        };
        document.body.innerHTML = `
            <div id="mailDetailModal">
                <div class="modal-dialog"></div>
            </div>
            <div id="container"></div>
        `;

        showMailDetailModal(event, app);
    });
    afterEach(() => {
        global.$ = jquery;
    });

    it('should add recipient as content of #task-id', () => {
        expect($('#task-id').html).toHaveBeenCalledWith('recipient')
    });
    it('should add email sender as content of #email-from', () => {
        expect($('#email-from').html).toHaveBeenCalledWith('email from')
    });
    it('should add email recipient as content of #email-to', () => {
        expect($('#email-to').html).toHaveBeenCalledWith('email to')
    });
    it('should call moment format', () => {
        expect(global.moment.utc().format).toHaveBeenCalledWith('MMMM Do YYYY, h:mm:ss a');
    });
    it('should add product id as content of #product-id', () => {
        expect($('#product-id').html).toHaveBeenCalledWith('product id')
    });
    it('should add product name as content of #product-name', () => {
        expect($('#product-name').html).toHaveBeenCalledWith('product name')
    });
    it('should add asset id as content of #asset-id', () => {
        expect($('#asset-id').html).toHaveBeenCalledWith('asset id')
    });
    it('should add request id as content of #request-id', () => {
        expect($('#request-id').html).toHaveBeenCalledWith('request id')
    });
    it('should add email content as content of #email-content', () => {
        expect($('#email-content').html).toHaveBeenCalledWith('email body')
    });
    it('should emit size with height set to 100', () => {
        expect(app.emit).toHaveBeenCalledWith('$size', {"height": 100})
    });
});

describe('populateDataTable', () => {
    let callback;
    const data = {
        length: 10,
        start: 0,
    };

    const res = {
        data: 'results', 
        recordsTotal: 12, 
        recordsFiltered: 12
    };

    beforeEach(() => {
        callback = jest.fn();
        jest.spyOn(global, 'fetch').mockReturnValue(Promise.resolve({
            json: () => Promise.resolve({
                results: 'results',
                count: 12
            })
        }));

        document.body.innerHTML = `
            <div id="loader-container"></div>
            <div id="settings"></div>
        `;

        populateDataTable(data, callback, '');
    });

    it('should populate DataTable', () => {
        expect(callback).toHaveBeenCalledWith(res);
    });
});

describe('toggleDisabledClassOnPageUp', () => {
    beforeEach(() => {
        document.body.innerHTML = `<div id="page-up"></div>`;
    });

    it('should add disabled class on page up', () => {
        toggleDisabledClassOnPageUp(10, 9);
        expect($('#page-up').attr('class')).toBe('disabled');
    });

    it('should remove disabled class on page up', () => {
        toggleDisabledClassOnPageUp(10, 20);
        expect($('#page-up').attr('class')).not.toBe('disabled');
     });
});

describe('toggleDisabledClassOnPageDown', () => {
    beforeEach(() => {
        document.body.innerHTML = `<div id="page-down"></div>`;
    });

    it('should add disabled class on page down', () => {
        toggleDisabledClassOnPageDown(0);
        expect($('#page-down').attr('class')).toBe('disabled');
    });

    it('should remove disabled class on page down', () => {
        toggleDisabledClassOnPageDown(10);
        expect($('#page-down').attr('class')).not.toBe('disabled');
    });
});

describe('createTable', () => {
    let table;
    beforeEach(() => {
        jest.spyOn(global, '$').mockReturnValue({
            DataTable: () => ({title: 'table'}),
            on: jest.fn()
        });

        table = createTable();
    });
    afterEach(() => {
        global.$ = jquery;
    });

    it('should return created table', () => {
        expect(table).toEqual({title: 'table'});
    });

    it('should set event $.on 3 times', () => {
        expect(global.$().on).toHaveBeenCalledTimes(3);
    });
});

describe('getProductLogo', () => {
    it('should return div with product logo', () => {
        expected = `<div class="td-product"><img src="/some/path" alt="Logo" height="22">
            <div>
                <div class="name">some product name</div>
                <div class="id">some id</div>
            </div>
        </div>`.replace(/ +</g, '<');

        const productLogo = getProductLogo('/some/path', '', { product_name: 'some product name', product_id: 'some id' }, '').replace(/ +</g, '<');
        expect(productLogo).toBe(expected);
    });
});

describe('getDate', () => {
    beforeEach(() => {
        const format = jest.fn();
        global.moment = {
            utc: () => ({
                format
            })
        };
    });

    it('should call moment format', () => {
        getDate(1670875686);
        expect(global.moment.utc().format).toHaveBeenCalledWith('MMMM Do YYYY, h:mm:ss a');
    });
});

describe('getVisibilityButton', () => {
    it('should return div with visibility button', () => {
        expected = `<button type="button" class="material-icons" data-mdb-toggle="modal" data-mdb-target="#mailDetailModal"
        data-mdb-whatever="some-id">visibility</button>`;

        const visibilityButton = getVisibilityButton('', '', { id: 'some-id' }, '');
        expect(visibilityButton).toBe(expected);
    });
});

describe('resend', () => {
    const id = 123;
    beforeEach(() => {
        jest.spyOn(global, '$').mockReturnValue({html: () => id});
        jest.spyOn(global, 'fetch').mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')
        }));
    });

   it('should call fetch with correct url', async () => {
       await resend();
       expect(global.fetch).toHaveBeenCalledWith(`/api/tasks/${id}/resend`, { method: 'POST', });
    });
});