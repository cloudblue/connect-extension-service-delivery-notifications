import createApp from '/static/js/toolkit.js';
const app = createApp({});

app.listen('$init', main);
$('#resend').click(resend);

export async function getEmailLogsList(limit, offset, search) {
    const response = await fetch(`/api/email_tasks?search=${search}&limit=${limit}&offset=${offset}`);
    let body = await response.json();
    return body;
}

async function main() {
    let offset = 0;
    let search = '';
    document.getElementById("EmailLogsTable").style.display = 'inline';
    var t = $('#task-list-table').DataTable({
        'paging': false,
        'searching': false,
        'info': false,
        'serverSide': true,
        'processing': true,
        'buttons': [
            'searchPanes'
        ],
        'ajax': async function (data, callback, settings) {

            const limit = $('#select-rows-per-page').val();
            let res = await getEmailLogsList(limit, offset, $('#search-input').val());
            let count = res.count;
            res = { 'data': res.results };
            if (offset <= 1) {
                $('#page-down').addClass('disabled');
            } else {
                $('#page-down').removeClass('disabled');
            }
            let pageMax = parseFloat(offset) + parseFloat(limit) - 1;
            if (pageMax >= count) {
                $('#page-up').addClass('disabled');
                pageMax = count;
            } else {
                $('#page-up').removeClass('disabled');
            }

            $('#page-total').html(count);
            $('#page-min').html(parseFloat(offset)+1);
            $('#page-max').html(pageMax);
            callback(res);
        },
        'columns': [
            { 'data': 'id' },
            {
                'data': 'product_logo', render: function (data, type, row, meta) {
                    return `<div class="td-product"><img src="${data}" alt="Logo" height="22"><div>
                        <div class="name">${row['product_name']}</div>
                        <div class="id">${row['product_id']}</div>
                    </div></div>`
                }
            },
            { 'data': 'email_to' },
            {
                'data': 'date', render: function (data, type, row, meta) {
                    return moment.utc(data).format('MMMM Do YYYY, h:mm:ss a');
                }
            },
            {
                'data': 'date', render: function (data, type, row, meta) {
                    return `<button type="button" class="material-icons" data-mdb-toggle="modal" data-mdb-target="#mailDetailModal"
            data-mdb-whatever="${row['id']}">visibility</button>`;
                }
            },
        ],
    });

    $('#search-input').keyup(function () {
        if ($(this).val().length==0 || $(this).val().length>3) {
            t.ajax.reload();
        }

    });

    $('#select-rows-per-page').change(function () {
        t.ajax.reload();
    });

    $('#page-down').click(function () {
        const limit = $('#select-rows-per-page').val();
        offset = (parseFloat(offset) - parseFloat(limit));
        if (offset < 0) offset = 0;
        t.ajax.reload();
    });

    $('#page-up').click(function () {
        const limit = $('#select-rows-per-page').val();
        offset = parseFloat(offset) + parseFloat(limit);
        t.ajax.reload();
    });

    const mailDetailModal = document.getElementById('mailDetailModal');
    mailDetailModal.addEventListener('show.mdb.modal', async (e) => {
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
        }
    });

    mailDetailModal.addEventListener('hide.mdb.modal', async (e) => {
        const container = document.getElementById('container');
        const height = container.offsetHeight;
        app.emit('$size', { height });
        t.destroy();
        main();
    });
    app.emit('$size', { height: 800 });
}

async function resend() {
    const id = $('#task-id').html();
    await fetch(`/api/tasks/${id}/resend`, { method: 'POST', });
}
