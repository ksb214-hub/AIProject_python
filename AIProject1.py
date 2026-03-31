from transformers import pipeline

chatbot = pipeline("text-generation", model="gpt2")

while True:
    user = input("나: ")

    if user.lower() == "exit":
        print("대화를 종료합니다.")
        break

    result = chatbot(user, max_length=50)

    generated = result[0]['generated_text']
    response = generated[len(user):]

    print("봇:", response.strip())