from celery import shared_task
from .models import Order


@shared_task
def process_order(order_id):
    print(f'Start processing order #{order_id}...')
    Order.objects.filter(id=order_id, status='pending').update(status='processing')
    print(f'Order #{order_id} status updated to processing')
    return f'Order #{order_id} processed'
