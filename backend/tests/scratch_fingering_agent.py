import asyncio

from app.services.agents.fingering import optimize_fingering


async def main():
    chords = ["F#m", "D", "A", "E"]

    print("=== 场景 1：支持的请求（power chord 换把位）===")
    result, explanation = await optimize_fingering(chords, "改成 5 品附近的 power chord，不要大跳")
    print("说明:", explanation)
    if result:
        for c in result:
            print(f"  {c.original} -> {c.display}, 指法 {c.fingering}, 把位 {c.position}")

    print()
    print("=== 场景 2：不支持的请求（换开放和弦把位）===")
    result, explanation = await optimize_fingering(chords, "帮我把木吉他版本的和弦换个把位")
    print("说明:", explanation)
    print("result:", result)


asyncio.run(main())
