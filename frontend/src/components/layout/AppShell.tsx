import { Sidebar } from "./Sidebar";

/**
 * 全局两栏壳层：左侧常驻边栏 + 右侧主内容区（随路由切换）。
 * 参照 ChatGPT 的布局模式——侧边栏承载导航/历史记录，
 * 不需要每个页面各自重复处理"怎么回到别的歌曲"。
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="h-screen flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
