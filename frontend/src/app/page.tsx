/**
 * 首页（产品文档 §15.1）：上传音频。
 * 上传成功后跳转 /songs/[id] 分析页。
 *
 * 产品文档提到的"选择目标（木吉他/电吉他/新手版）"未实现：
 * 后端 generate_arrangements 端点不接受目标参数，一次性生成全部版本，
 * 不需要前端在上传前先做选择。
 */
import { SongList } from "@/components/upload/SongList";
import { UploadForm } from "@/components/upload/UploadForm";

export default function HomePage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col items-center gap-8 px-6 py-24 text-center">
      <div className="flex flex-col items-center gap-6">
        <h1 className="text-4xl font-bold">FretAI</h1>
        <p className="text-lg text-gray-500">
          上传任意歌曲，FretAI 自动生成你能弹的吉他版本。
        </p>
        <UploadForm />
      </div>
      <SongList />
    </main>
  );
}
