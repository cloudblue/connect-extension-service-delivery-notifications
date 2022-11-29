import createApp from '/static/js/toolkit.js';

$(window).on('load', async () => {
    setupEvents();
    await refresh();
});

export async function getRules() {
    const response = await fetch('/api/rules');
    const body = await response.json();
    return body;
}

export async function getSettings() {
    const response = await fetch('/api/settings');
    const body = await response.json();
    return body;
}

export async function getRule(id) {
    const response = await fetch(`/api/rules/${id}`);
    const body = await response.json();
    return body;
}

export async function getRulesProducts() {
    const response = await fetch('/api/products');
    const body = await response.json();
    return body;
}

async function deleteRule() {
    const id = $('#rule-id-delete').val();
    await fetch(`/api/rules/${id}`, { method: 'DELETE', });
    refresh();
}

async function createUpdateRule() {
    const ruleId = $('#rule-id-update').val();
    const enabled = $('#enabled').is(':checked');
    const productId = ruleId ? $('#product-id-update').val() : $("#product-id-select option:selected").val();

    const responseProd = await fetch(`/api/products/${productId}`);
    const product = await responseProd.json();
    let icon;
    if (product['logo']!= null){
        icon = product['icon'];
    } else {
        icon = './images/product.svg';
    }
    const payload = JSON.stringify({
        "product_id": productId,
        "product_name": product['name'],
        "product_logo": icon,
        "enabled": enabled,
        "message": $('#message-text').val()
    });

    let url = null;
    let method = null;

    if (ruleId) {
        url = `/api/rules/${ruleId}`;
        method = 'PUT'
    } else {
        url = `/api/rules`;
        method = 'POST'
    }
    try {
        await fetch(
            url,
            {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: payload
            }
        );
        $('#rule-id-update').val('');
        refresh();
    } catch (e){alert(e)}
}

export async function refreshRules() {
    $('#ruleBody').empty();
    const rules = await getRules();
    if (rules.length == 0) {
        $('#ruleBody').append(
            '<tr><td colspan="4" style="text-align: center"><strong>No rules found</strong></td></tr>'
        );
        return;
    }
    rules.forEach(rule => {
        const row = $('<tr>');
        row.append(`<td>${rule.id}</td>`);
        row.append(`
        <td class="td-product">
            <img src="./images/product.svg" alt="Logo">
            <div>
                <div class="name">${rule.product_name}</div>
                <div class="id">${rule.product_id}</div>
            </div>
        </td>
        `);
        if (rule.enabled) {
            row.append('<td><span class="enabled"></span>Enabled</td>');
        } else {
            row.append('<td><span class="disabled"></span>Disabled</td>');
        }

        row.append(`
            <td>
                <button
                    type="button"
                    class="material-icons btn-secondary"
                    data-mdb-toggle="modal"
                    data-mdb-target="#addModifyModal"
                    data-mdb-whatever="${rule.id}">
                    edit
                </button>
                <button
                    type="button"
                    class="material-icons btn-danger"
                    data-mdb-toggle="modal"
                    data-mdb-target="#deleteModal"
                    data-mdb-whatever="${rule.id}">
                    delete
                </button>
            </td>  
        `);
        $('#ruleBody').append(row);
    });
}

export async function populateProductsDropdown() {
    $('#product-id-select').empty();
    const products = await getRulesProducts();
    products.forEach(product => {
        if (!product.used) {
            $('#product-id-select').append(
                `<option value="${product.id}">${product.name}</option>`
            );
        }
    });
}

export async function showSeeConfDialog(e) {
    const settings = await getSettings();
    $('#email_sender').html(settings.email_sender);
    $('#name').html(settings.name);
}

export async function showDeleteDialog(e) {
    const button = $(e.relatedTarget);
    const ruleId = button.attr('data-mdb-whatever');
    const rule = await getRule(ruleId);
    $('#deleteModal .modal-body').html(`Are you sure delete the rule associated <br> to the product: ${rule['product_name']}?`);
    $('#rule-id-delete').val(ruleId);
}

async function showAddModifyDialog(e) {
    $('#addModifyModalDiv').hide();
    const button = $(e.relatedTarget);
    const ruleId = button.attr('data-mdb-whatever');
    if (!ruleId) {
        await populateProductsDropdown();
        $('#productIdLabel').hide();
        $('#productDropdown').show();
        $('#header-content').text('Create Rule');
        $('#add-modify-label-button').text('ADD');
        $('#message-text').load('example.md', updateMD);
        $('#productIdLabel').text('');
    } else {
        const rule = await getRule(ruleId);
        $('#productDropdown').hide();
        const textTitle = `Modify Rule for: ${rule['product_name']}`;
        $('#header-content').text(textTitle);
        $('#add-modify-label-button').text('SAVE');
        $('#enabled').prop('checked', rule['enabled'] == true);
        $('#rule-id-update').val(ruleId);
        $('#product-id-update').val(rule['product_id']);
        $('#message-text').val(rule['message']);
        await updateMD();
    }
    $('#addModifyModalDiv').show();
}

export async function refresh() {
    const products = await getRulesProducts();
    let productsAvailable = false;
    products.forEach(product => {
        if (!product.used) {
            productsAvailable = true;
        }
    });

    $('#buttonAdd').prop('disabled', !productsAvailable);
    await refreshRules();
}

function setupEvents() {
    $('#deleteModal').on('show.mdb.modal', showDeleteDialog);
    $('#addModifyModal').on('show.mdb.modal', showAddModifyDialog);
    $('#seeConfModal').on('show.mdb.modal', showSeeConfDialog);
    $('#updateRule').click(createUpdateRule);
    $('#deleteRule').click(deleteRule);
    $('#message-text').on('input', updateMD);
}

async function updateMD() {
    let preview = $('#message-text').val();
    preview = markdown.toHTML(preview);
    $('#previewMD').html(preview);
}

const app = createApp({});
app.listen('$init', async () => {
    app.emit('$size', { height: 800 });
});
