import {
    getSettings,
    getRules,
    getRule,
    getRulesProducts,
    refreshRules,
    populateProductsDropdown,
    showSeeConfDialog,
    showDeleteDialog,
    refresh,
} from '../cen/static/js/settings.js';

let expected;

describe('getSettingsTest', () => {
    let settings;
    beforeEach(async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve({ email_sender: 'test@example.email', name: 'Test' }),
        }));
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

describe('getRulesTest', () => {
    it('should return rules', async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve('OK')
        }));
        const rules = await getRules();
        expect(rules).toBe('OK');
    });
});

describe('getRuleTest', () => {
    it('should return rule', async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve({
                product_id: 'PRD-000',
                product_name: 'product01',
                product_logo: 'img.png',
                message: 'message',
                enabled: true,
            })
        }));
        const rule = await getRule('RUL-000');
        expect(rule.product_id).toBe('PRD-000');
        expect(rule.product_name).toBe('product01');
        expect(rule.product_logo).toBe('img.png');
        expect(rule.message).toBe('message');
        expect(rule.enabled).toBe(true);
    });
});

describe('getRulesProductsTest', () => {
    it('should return rule', async () => {
        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve([
                {
                    'id': 'PRD-000',
                    'name': 'product01',
                    'icon': 'img.png',
                    'used': true
                }
            ])
        }));
        const rule = await getRulesProducts();
        expect(rule['0'].id).toBe('PRD-000');
        expect(rule['0'].name).toBe('product01');
        expect(rule['0'].icon).toBe('img.png');
        expect(rule['0'].used).toBe(true);
    });
});

describe('refreshRulesTest', () => {
    it('should return "No rules found" row', async () => {
        document.body.innerHTML = '<table id="ruleBody">Some text</table>';

        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve([]),
        }));

        await refreshRules();

        expect($('#ruleBody').text()).toBe('No rules found');
    });

    it('should return filled row', async () => {
        document.body.innerHTML = '<table id="ruleBody">Some text</table>';

        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve([{
                id: 'ID',
                product_id: 'PRD-000',
                product_name: 'product01',
                enabled: true,
            }]),
        }));

        expected = `<tr><td>ID</td>
        <td class="td-product">
            <img src="./images/product.svg" alt="Logo">
            <div>
                <div class="name">product01</div>
                <div class="id">PRD-000</div>
            </div>
        </td>
        <td><span class="enabled"></span>Enabled</td>
            <td>
                <button type="button" class="material-icons btn-secondary" data-mdb-toggle="modal" data-mdb-target="#addModifyModal" data-mdb-whatever="ID">
                    edit
                </button>
                <button type="button" class="material-icons btn-danger" data-mdb-toggle="modal" data-mdb-target="#deleteModal" data-mdb-whatever="ID">
                    delete
                </button>
            </td>  
        </tr>`;

        await refreshRules();

        expect($('#ruleBody').html()).toBe(expected);
    });
});

describe('populateProductsDropdownTest', () => {
    it('should replace product options in select', async () => {
        document.body.innerHTML = `
           <div>
               <select id="product-id-select">
                   <option selected>PRO-000</option>
                   <option>PRO-001</option>
               </select>
            </div>
       `;

        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve([
                {
                    'id': 'PRD-002',
                    'name': 'product02',
                },
                {
                    'id': 'PRD-003',
                    'name': 'product03',
                }
            ])
        }));

        expected = `<option value="PRD-002">product02</option><option value="PRD-003">product03</option>`;

        await populateProductsDropdown();

        expect($('#product-id-select').html()).toBe(expected);
    });
});

describe('showSeeConfDialogTest', () => {
   it('should add e-mail to settings', async () => {
      document.body.innerHTML = `
      <div>
          <div id="email_sender"></div>
          <div id="name"></div>
      </div>
      `;

       global.fetch.mockReturnValue(Promise.resolve({
           json: () => Promise.resolve({
               email_sender: 'e-mail sender',
               name: 'name',
           })
       }));

       await showSeeConfDialog();

       expect($('#email_sender').text()).toBe('e-mail sender');
   });

    it('should add name to settings', async () => {
        document.body.innerHTML = `
      <div>
          <div id="email_sender"></div>
          <div id="name"></div>
      </div>
      `;

        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve({
                email_sender: 'e-mail sender',
                name: 'name',
            })
        }));

        await showSeeConfDialog();

        expect($('#name').text()).toBe('name');
    });
});

describe('showDeleteDialogTest', () => {
   it('should show delete dialog', async () => {
       document.body.innerHTML = `<div id="container">
           <button id="delete-button" data-mdb-whatever="RULE-ID"></button>
           <div id="deleteModal">
               <div class="modal-body"></div>
           <input type="hidden" id="rule-id-delete" value="">
           </div>
       </div>`;

       global.fetch.mockReturnValue(Promise.resolve({
           json: () => Promise.resolve({
               product_name: 'product01',
           })
       }));

       expected = `
           <button id="delete-button" data-mdb-whatever="RULE-ID"></button>
           <div id="deleteModal">
               <div class="modal-body">Are you sure delete the rule associated <br> to the product: product01?</div>
           <input type="hidden" id="rule-id-delete" value="RULE-ID">
           </div>
       `;

       await showDeleteDialog({relatedTarget: '#delete-button'});

       expect($('#container').html()).toBe(expected);
   });
});

describe('refreshTest', () => {
    it('should disable add button if there any unavailable products', async () => {
        document.body.innerHTML = `<button id="buttonAdd" disabled></button>`;

        global.fetch.mockReturnValue(Promise.resolve({
            json: () => Promise.resolve([
                {used: false},
            ])
        }));

        await refresh();

        expect($('#buttonAdd').attr('disabled')).toBeFalsy();
    });
});
