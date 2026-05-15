from ollama_wrapper import create_ollama_api

api = create_ollama_api()

def image_test():
    print("=" * 55)
    print("1. GENERATE + 多图（你的方案）")
    print("=" * 55)
    for chunk in api.chat(
        prompt='Describe both images in one sentence. Image 1:<image> and Image 2:<image>',
        model='gemma4:e4b',
        image_paths=[
            r'D:\08_tmp\02_media\media-arcitles\4_mathType\image.png',
            r'D:\08_tmp\02_media\media-arcitles\4_mathType\image-1.png',
        ],
        stream=True
    ):
        print(chunk, end="", flush=True)
    print()
    print()



def chat_test():
    print("=" * 55)
    print("2. CHAT + 系统提示词")
    print("=" * 55)
    r = api.chat(
        model="gemma4:e4b",
        prompt="用一句话解释光速为什么是极限",
        system_prompt="你是物理学家，回答控制在30字以内",
    )
    print(r)
    print()

def chat_single_image():
    print("=" * 55)
    print("3. CHAT + 单图")
    print("=" * 55)
    r = api.chat(
        model="gemma4:e4b",
        prompt="这张截图里有什么关键信息？",
        image_path=r"D:\08_tmp\02_media\media-arcitles\4_mathType\image.png",
        max_tokens=200,
    )
    print(r)
    print()

def chat_stream():
    print("=" * 55)
    print("4. CHAT + 流式")
    print("=" * 55)
    for chunk in api.chat(
        prompt="用10个字描述Python",
        model="gemma4:e4b",
        stream=True,
    ):
        print(chunk, end="", flush=True)
    print() 

if __name__ == "__main__":
    image_test()
    #chat_test()
    #chat_single_image()
    #chat_stream()