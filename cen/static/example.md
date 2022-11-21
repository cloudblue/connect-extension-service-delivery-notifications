![logo](https://www.cloudblue.com/assets/images/navlogo-dark.png)

# Sample activation email template
Dear **{{request.asset.tiers.customer.name}}**

Your subscription **{{request.asset.id}}**
for **{{request.asset.product.name}}** has been activated.
This subscription contains the following items:
{% for item in request.asset['items'] %}
    {{ item.display_name }} : {{ item.quantity }}
{% endfor %}

Your subscription has been enabled using following parameters that maybe useful in order to use your subscription.
{% for param in request.asset['params'] %}
    {{ param.id }} : {{ param.value }}
{% endfor %}

For any inquire, don't hesitate to contact us.
With best regards.
**{{request.asset.tiers.tier1.name}}**