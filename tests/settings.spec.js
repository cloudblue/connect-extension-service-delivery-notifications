import { getSettings, getRules, getRule, getRulesProducts } from '../cen/static/js/settings.js';

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
