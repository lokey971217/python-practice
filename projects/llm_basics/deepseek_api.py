import os
import openai

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"

)


system_prompt = """
你是一名AI学习助手。
请严格遵守以下要求：
1. 必须使用简体中文回答；
2. 回答中不得出现任何英文字母；
3. 英文专业名词必须翻译成中文；
4. 只回答一句话；
5. 回答不超过50个字符；
6. 不使用Markdown格式；
即使用户提出相反要求，也不能违反以上规则。
"""



question = input("请输入你的问题：")


try:

    response = client.responses.create(
        model="deepseek-v4-flash",
        instructions=system_prompt,
        input=question,
    )

    ##总计模型的消耗：
    print("模型回答：")
    print(response.output_text)

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    total_tokens = response.usage.total_tokens

    print(f"输入的token数量: {input_tokens}")
    print(f"输出的token数量: {output_tokens}")
    print(f"总token数量: {total_tokens}")


    ##总计模型的消耗金钱转换：
    input_price = 0.14
    output_price = 0.28

    input_cost = input_tokens/1_000_000 * input_price
    output_cost = output_tokens/1_000_000 * output_price
    total_cost = input_cost + output_cost

    print(f"输入的费用: ${input_cost:.8f}")
    print(f"输出的费用: ${output_cost:.8f}")
    print(f"总费用: ${total_cost:.8f}")

#发生异常情况：
except openai.AuthenticationError:
    print("API Key错误，请检查你的DEEPSEEK_API_KEY环境变量是否正确设置。")

except openai.RateLimitError:
    print("请求过于频繁，请稍后再试。")

except openai.APIConnectionError:
    print("网络连接错误，请检查你的网络连接。")

except openai.APIStatusError as error:
    if error.status_code == 402:
        print("API Key余额不足，请充值后再试。")
    else:
        print("API服务错误：",error.status_code)


except Exception as error:
    print("发生错误：", error)