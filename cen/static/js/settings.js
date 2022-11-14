import createApp from '/static/js/toolkit.js';
const app = createApp({});

async function getSettings() {
    const response = await fetch('/api/settings');
    const body = await response.json();
    return body;
}

const body = await getSettings(); 
$('#email_sender').html(body.email_sender);
$('#name').html(body.name);
