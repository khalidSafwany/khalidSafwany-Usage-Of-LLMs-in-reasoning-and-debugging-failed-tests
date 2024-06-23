from openai import OpenAI

# replace with your openai api-key
client = OpenAI(api_key="")


def get_answer(file_path: str, file_name:str):
    assistant = client.beta.assistants.create(
        name="Scratch Debug Assistant",
        instructions="You are an expert Scratch teacher."
                     " Use your knowledge base to answer questions about the failed tests in the scratch programs.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    vector_store = client.beta.vector_stores.create(name="Scratch Statements")

    file_paths = [file_path]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)

    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    message_file = client.files.create(
        file=open(file_path, "rb"), purpose="assistants"
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "simply explain for new Scratch learner, why did the test fail in this program?",
                # Attach the new file to the message.
                "attachments": [
                    {"file_id": message_file.id, "tools": [{"type": "file_search"}]}
                ],
            }
        ]
    )

    print(thread.tool_resources.file_search)

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")
    answer_file_path = 'Answers/' + file_name + '.txt'
    with open(answer_file_path, 'w') as file:
        file.write(message_content.value)

