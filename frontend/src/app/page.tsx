/**
 * 首页（产品文档 §15.1）：上传音频，作为右侧主内容区的"空状态"。
 * 历史记录已移到左侧常驻边栏（Sidebar），这里不再重复展示。
 * 上传成功后跳转 /songs/[id] 分析页。
 *
 * 产品文档提到的"选择目标（木吉他/电吉他/新手版）"未实现：
 * 后端 generate_arrangements 端点不接受目标参数，一次性生成全部版本，
 * 不需要前端在上传前先做选择。
 */
import { UploadForm } from "@/components/upload/UploadForm";

export default function HomePage() {
  return (
    <div className="flex h-full min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <h1 className="text-3xl font-semibold tracking-tight text-gray-900">FretAI</h1>
      <p className="text-base text-gray-500">
        上传任意歌曲，FretAI 自动生成你能弹的吉他版本。
      </p>
      <UploadForm />
    </div>
  );
}
