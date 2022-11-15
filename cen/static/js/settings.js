import createApp from '/static/js/libs/toolkit.js';


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

createApp({}).then(function() {settingsPage.main();});