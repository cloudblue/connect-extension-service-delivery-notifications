import createApp from '/static/js/toolkit.js';
const createdApp = createApp({});

createdApp.listen('$init', () => main(createdApp));
$('#resend').click(resend);

const dataTableConfig = {
    'paging': true,
    'searching': true,
    'lengthChange': false,
    'info': false,
    'serverSide': true,
    'processing': true,
    'buttons': [
        'searchPanes'
    ],
    'dom': 't',
    'ajax': populateDataTable,
    'columns': [
        { 'data': 'id' },
        {
            'data': 'product_logo', render: getProductLogo
        },
        { 'data': 'email_to' },
        {
            'data': 'date', render: getDate
        },
        {
            'data': 'date', render: getVisibilityButton
        },
    ],
};

export async function getEmailLogsList(limit, offset, search) {
    const response = await fetch(`/api/email_tasks?search=${search}&limit=${limit}&offset=${offset}`);
    let body = await response.json();
    document.getElementById("loader-container").style.display = 'none';
    document.getElementById("settings").style.display = 'block';
    return body;
};

export function main(app) {
    const table = createTable();

    const mailDetailModal = document.getElementById('mailDetailModal');
    mailDetailModal.addEventListener('show.mdb.modal', showMailDetailModal);

    mailDetailModal.addEventListener('hide.mdb.modal', hideMailDetailModal(app, table));
    app.emit('$size', { height: 800 });
};

export function hideMailDetailModal(app, table) {
    return (e) => {
        table.page( 'first' ).draw( 'page' );
        app.emit('$size', { height: 800 });
    };
};

export async function showMailDetailModal(e, app) {
    const mailDetailModal = document.getElementById('mailDetailModal');
    const button = e.relatedTarget;
    const recipient = button.getAttribute('data-mdb-whatever');
    const response = await fetch(`/api/email_task/${recipient}`);
    const body = await response.json();
    const dateEmail = moment.utc(body['date']).format('MMMM Do YYYY, h:mm:ss a');

    $('#task-id').html(recipient);
    $('#email-from').html(body['email_from']);
    $('#email-to').html(body['email_to']);
    $('#date').html(dateEmail);
    $('#product-id').html(body['product_id']);
    $('#product-name').html(body['product_name']);
    $('#asset-id').html(body['asset_id']);
    $('#request-id').html(body['request_id']);
    $('#email-content').html(body['body']);

    const modalBody = mailDetailModal.getElementsByClassName('modal-dialog')[0];
    const container = document.getElementById('container');

    if (modalBody.offsetHeight >= container.offsetHeight) {
        const height = modalBody.offsetHeight + 100;
        app.emit('$size', { height });
    };
};

export async function populateDataTable(data, callback, settings) {
    const limit = data.length;
    const offset = data.start;
    let res = await getEmailLogsList(limit, offset, $('#search-input').val());
    let count = res.count;
    res = { 'data': res.results, 'recordsTotal': count, 'recordsFiltered': count };
    toggleDisabledClassOnPageDown(offset);
    let pageMax = parseFloat(offset) + parseFloat(limit);
    pageMax = toggleDisabledClassOnPageUp(pageMax, count);

    $('#page-total').html(count);
    $('#page-min').html(parseFloat(offset) + 1);
    $('#page-max').html(pageMax);
    callback(res);
};

export function toggleDisabledClassOnPageUp(pageMax, count) {
    if (pageMax >= count) {
        $('#page-up').addClass('disabled');
        pageMax = count;
    } else {
        $('#page-up').removeClass('disabled');
    }
    return pageMax;
};

export function toggleDisabledClassOnPageDown(offset) {
    if (offset <= 1) {
        $('#page-down').addClass('disabled');
    } else {
        $('#page-down').removeClass('disabled');
    };
};

export function createTable() {
    const table = $('#task-list-table').DataTable(dataTableConfig);

    $('#search-input').on('keyup', function () {
        if ($(this).val().length > 3 || $(this).val() === '') {
            table.ajax.reload();
        };
    });

    $('#page-down').on('click', function () {
        table.page( 'previous' ).draw( 'page' );
    });

    $('#page-up').on('click', function () {
        table.page( 'next' ).draw( 'page' );
    });

    return table;
};

export function getProductLogo(data, type, row, meta) {
    return `<div class="td-product"><img src="${data}" alt="Logo" height="22">
                <div>
                    <div class="name">${row['product_name']}</div>
                    <div class="id">${row['product_id']}</div>
                </div>
            </div>`;
};

export function getDate(data, type, row, meta) {
    return moment.utc(data).format('MMMM Do YYYY, h:mm:ss a');
};

export function getVisibilityButton(data, type, row, meta) {
    return `<button type="button" class="material-icons" data-mdb-toggle="modal" data-mdb-target="#mailDetailModal"
        data-mdb-whatever="${row['id']}">visibility</button>`;
};

export async function resend() {
    const id = $('#task-id').html();
    await fetch(`/api/tasks/${id}/resend`, { method: 'POST', });
};
