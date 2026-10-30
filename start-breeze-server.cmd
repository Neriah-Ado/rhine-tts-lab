@echo off
rem Breeze TTS 2 fast-path server launcher (RTX 5080, Windows native)
rem First cold start compiles CUDA graphs (~14 min); later starts reuse cache (~1-2 min).
rem Env vars below are required: static CUDA launcher crashes on Windows,
rem and cache dirs must be SHORT paths (kernel names are ~156 chars; C:\Temp paths exceed MAX_PATH 260).
set TORCHINDUCTOR_USE_STATIC_CUDA_LAUNCHER=0
set TORCHINDUCTOR_CACHE_DIR=H:\ic
set TRITON_CACHE_DIR=H:\tc
set TORCHINDUCTOR_COMPILE_THREADS=1
set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /d "H:\Vibe coding\breeze-tts"
.venv\Scripts\python.exe -m breeze_infer.api "H:\Vibe coding\breeze-tts-2" --host 127.0.0.1 --port 7860 --fast-all
