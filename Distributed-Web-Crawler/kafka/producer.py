from confluent_kafka import Producer
import json

# KAFKA CONFIG

config = {
    'bootstrap.servers': '127.0.0.1:9092'
}

producer = Producer(config)

# DELIVERY REPORT

def delivery_report(err, msg):

    if err is not None:
        print('Delivery failed:', err)

    else:
        print(
            f'Sent to {msg.topic()} '
            f'[{msg.partition()}]'
        )

# SEND URLS

urls = [
    "https://books.toscrape.com"
]

for url in urls:

    data = {
        "url": url
    }

    producer.produce(
        'crawler-topic',
        json.dumps(data).encode('utf-8'),
        callback=delivery_report
    )

    producer.poll(1)

# Flush messages
producer.flush()

print("\nAll URLs sent successfully")