import argparse as ap
import paths

from openai import OpenAI


def get_batch_id():
    with open(paths.BATCH_ID_FILE, 'r') as f:
        return f.read()


def create_batch_request(client):
    # TODO prevent creation of new one if old batch is still running or hasn't been retrieved
    print('creating batch request')
    batch_input_file = client.files.create(
        file=open(paths.BATCH_CARDS, "rb"),
        purpose="batch"
    )

    batch_input_file_id = batch_input_file.id
    print(f'batch request created: {batch_input_file_id}')

    batch_info = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/embeddings",
        completion_window="24h",
    )


    print(f'batch request create finished')
    print(f'batch request id {batch_info.id}')
    with open(paths.BATCH_ID_FILE, 'w') as f:
        f.write(batch_info.id)


def retrieve_batch_response(client):
    batch_info = client.batches.retrieve(get_batch_id())
    counts = batch_info.request_counts
    percent_done = 100 * counts.completed / counts.total
    percent_failed = 100 * counts.failed / counts.total
    print(f'current batch status "{batch_info.status}", {percent_done:1f}% done, {percent_failed:1f}% failed')

    if batch_info.status == 'completed':
        print(f'batch finish, retrieving reponse')
        paths.RESPONSE_DIRC.mkdir(parents=True, exist_ok=True)

        if output_file := batch_info.output_file_id:
            file_response = client.files.content(output_file)
            with open(paths.RESPONSE_FILE, 'w') as f:
                f.write(file_response.text)

        if error_file := batch_info.error_file_id:
            file_response = client.files.content(error_file)
            with open(paths.ERROR_FILE, 'w') as f:
                f.write(file_response.text)
        
        print(f'finished retrieving reponse')


def list_batch_requests(client):
    for batch in client.batches.list(limit=1):
        print(batch)


def cancel_batch_request(client):
    batch_id = get_batch_id()
    print(f'cancelling {get_batch_id()}')
    client.batches.cancel(batch_id)


def get_args():
    parser = ap.ArgumentParser()
    parser.add_argument('action')
    return parser.parse_args()


if __name__ == '__main__':
    with open('OPENAI_SECRET_KEY', 'r') as f:
        client = OpenAI(api_key=f.read())

    match get_args().action:
        case 'create':
            create_batch_request(client)
        case 'retrieve':
            retrieve_batch_response(client)
        case 'cancel':
            cancel_batch_request(client)
        case 'list':
            list_batch_requests(client)
        case a:
            raise ValueError(f'unsupported action {a}')
