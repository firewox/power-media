from lmstudio_wrapper import LMStudioAPI, create_lmstudio_api


def demo_lmstudio():
    api = create_lmstudio_api()

    print("=== 纯文本（流式） ===")
    for chunk in api.chat("用中文简单介绍一下你自己", stream=True):
        print(chunk, end="", flush=True)
    print()
    print()


def demo_single_image():
    print("=== 单图内联（流式） ===")
    api = create_lmstudio_api()
    img = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image.png"
    for chunk in api.chat(
        "这是图片：<image>，请描述它的内容",
        image_path=img,
        stream=True,
    ):
        print(chunk, end="", flush=True)
    print()
    print()


def demo_multi_image():
    print("=== 多图内联对比（流式） ===")
    api = create_lmstudio_api()
    img_a = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image.png"
    img_b = r"D:\08_tmp\02_media\media-arcitles\4_mathType\image-1.png"
    for chunk in api.chat(
        "这是图片1：<image>，这是图片2：<image>，两者有什么不同？",
        image_paths=[img_a, img_b],
        stream=True,
    ):
        print(chunk, end="", flush=True)
    print()
    print()


def demo_system_prompt():
    print("=== System Prompt ===")
    api = create_lmstudio_api()
    result = api.chat(
        prompt="你是谁？",
        system_prompt="你是一个猫娘，用喵结尾",
    )
    print(result)
    print()


def demo_temperature():
    print("=== Temperature 对比 ===")
    api = create_lmstudio_api()
    for temp in [0.0, 1.0]:
        result = api.chat(
            prompt="讲一个笑话",
            temperature=temp,
            max_tokens=100,
        )
        print(f"[temperature={temp}] {result}")
    print()


if __name__ == "__main__":
    demo_lmstudio()
    # demo_single_image()
    # demo_multi_image()
    # demo_system_prompt()
    # demo_temperature()
