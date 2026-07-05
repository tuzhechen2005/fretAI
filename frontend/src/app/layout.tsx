import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FretAI",
  description: "不是只告诉你是什么和弦，而是告诉你怎么弹。",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
