/**
 * 首页（产品文档 §15.1）：上传音频 + 选择目标（木吉他/电吉他/新手版）。
 * 上传成功后跳转 /songs/[id] 分析页。
 */
export default function HomePage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col items-center gap-6 px-6 py-24 text-center">
      <h1 className="text-4xl font-bold">FretAI</h1>
      <p className="text-lg text-gray-500">
        上传任意歌曲，FretAI 自动生成你能弹的吉他版本。
      </p>
      {/* TODO: <UploadDropzone /> 上传组件 + 目标选择 */}
    </main>
  );
}
