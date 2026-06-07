from lmstudio_wrapper import LMStudioAPI

client = LMStudioAPI(model="google/gemma-4-e4b")


def chat_text():
    print("=== 纯文本 ===")
    for chunk in client.chat("用中文简单介绍一下你自己", stream=True):
        print(chunk, end="", flush=True)    
    print()


def chat_single_image():
    print("=== 单图内联（流式） ===")
    img1 = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image.png"
    for chunk in client.chat(
        "这是图片：<image>，请描述它的内容",
        image_path=img1,
        stream=True
    ):
        print(chunk, end="", flush=True)
    print()
    print()


def chat_multi_image():
    print("=== 多图内联对比（流式） ===")
    img_a = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image.png"
    img_b = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image-1.png"
    for chunk in client.chat(
        "这是图片1：<image>，这是图片2：<image>，两者有什么不同？",
        image_paths=[img_a, img_b],
        stream=True
    ):
        print(chunk, end="", flush=True)
    print()
    print()


if __name__ == "__main__":
    chat_text()
    #chat_single_image()
    #chat_multi_image()
