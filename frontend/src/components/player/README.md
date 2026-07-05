# player/

音频播放相关组件（Web Audio API）：

- `AudioPlayer.tsx` — 播放/暂停/进度，暴露 currentTime 给时间轴做和弦高亮
- `WaveformView.tsx` — 波形渲染（canvas），点击跳转
- `PlayerControls.tsx` — 变速（0.5x-1x）、A-B 循环、按小节跳转

MVP 变速可用 `<audio>.playbackRate`；变调（音高不变速）属 Phase 2。
