from transformers import pipeline

chatbot = pipeline("text-generation", model="gpt2")

while True:
    user = input("나: ")
    result = chatbot(user, max_length=50)
    print("봇:", result[0]['generated_text'])