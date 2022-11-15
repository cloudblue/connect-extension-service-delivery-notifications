import createApp from '/static/js/toolkit.js';
const app = createApp({});

const settingsPage ={
    async getSettings() {
        const response = await fetch('/api/settings');
        const body = await response.json();
        return body;
    },

    async main() {
        const settings = await this.getSettings();
        $('#email_sender').html(settings.email_sender);
        $('#name').html(settings.name);
    },
}

export default settingsPage;

settingsPage.main();