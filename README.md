# English Daily Coach — Discord Bot

Một bot Discord dẫn bạn qua vòng **Input → Understand → Recall → Use → Review** mỗi ngày:
10 từ vựng, paraphrase practice, IELTS writing sample có annotation, active-recall quiz,
spaced-repetition review, và weekly progress report.

## 1. Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## 2. Cấu hình

```bash
copy env.example .env
```

Điền vào `.env`:

- `DISCORD_BOT_TOKEN` — token bot từ Discord Developer Portal (xem hướng dẫn cấp quyền bên dưới).
- `DAILY_CHANNEL_ID` — ID kênh nơi bot tự động đăng bài học mỗi ngày (bật Developer Mode → chuột phải kênh → Copy Channel ID).
- `GUILD_ID` — ID server của bạn, để slash command sync tức thì thay vì chờ ~1 giờ.
- `DATABASE_URL` — connection string PostgreSQL, dạng `postgresql+asyncpg://user:pass@host:5432/dbname`.
- `LLM_PROVIDER` — `gemini` (mặc định, free tier tốt) hoặc `ollama` (100% free, chạy local).
  - Gemini: lấy `GEMINI_API_KEY` miễn phí tại https://aistudio.google.com/apikey
  - Ollama: cài https://ollama.com, chạy `ollama pull llama3.1`, để `OLLAMA_HOST`/`OLLAMA_MODEL` trỏ đúng.

## 3. Tạo bot & cấp quyền trên Discord Developer Portal

1. https://discord.com/developers/applications → **New Application**.
2. Tab **Bot** → **Reset Token** → copy vào `DISCORD_BOT_TOKEN`.
3. Vẫn ở tab **Bot**, bật **Privileged Gateway Intents**:
   - ✅ MESSAGE CONTENT INTENT (bắt buộc — bot đọc câu trả lời của bạn)
   - ✅ SERVER MEMBERS INTENT
4. Tab **OAuth2 → URL Generator**:
   - Scopes: ✅ `bot`, ✅ `applications.commands`
   - Bot Permissions: Send Messages, Send Messages in Threads, Embed Links, Read Message History, Add Reactions, Use Slash Commands, Manage Messages (tuỳ chọn)
   - Copy URL sinh ra ở cuối trang → mở → chọn server → Authorize.

## 4. Chạy bot

```bash
python -m bot.main
```

Lần đầu chạy sẽ tự tạo bảng trong PostgreSQL. Slash command sẽ xuất hiện trong server ngay lập tức nếu bạn có set `GUILD_ID`.

## 5. Lệnh có sẵn (MVP)

| Command       | Mô tả                                                              |
|---------------|---------------------------------------------------------------------|
| `/daily`      | Lấy bài học hôm nay: 10 từ vựng + IELTS writing sample có annotation |
| `/paraphrase` | Luyện paraphrase 1 câu, được chấm điểm + gợi ý Band 7+ alternative   |
| `/writing`    | Xem đề + sample, có thể thử viết câu trả lời để được check lỗi      |
| `/quiz`       | Active-recall challenge 5 câu hỏi từ bài học hôm nay                 |
| `/review`     | Ôn lại các từ đang yếu/đang học (nút I know / Almost / Don't know)   |
| `/quick`      | Streak Saver — ôn 3 từ yếu trong 2-3 phút khi bận                    |
| `/progress`   | Weekly report: từ đã học, từ còn yếu, lỗi hay gặp, streak            |

Bot tự động đăng "Daily Drop" vào `DAILY_CHANNEL_ID` mỗi ngày lúc `DAILY_HOUR:DAILY_MINUTE`
(theo `TIMEZONE`), và sẽ không gửi trùng nếu bài học hôm đó đã tồn tại (kể cả khi bot restart nhiều lần).

## 6. Nguồn từ vựng (data/vocabulary/)

Thay vì để LLM tự nghĩ từ mới mỗi ngày (dễ lặp từ, sai band, lệch chủ đề), bot đọc từ
một **word bank** đã soạn sẵn trong `data/vocabulary/*.json`, mỗi file là 1 chủ đề
(environment, education, technology, health, economy, society_and_culture,
crime_and_law, work_and_career — 15 từ/chủ đề, 120 từ). Mỗi ngày bot lấy 10 từ tiếp theo
trong bank chưa từng dạy, rồi mới gọi LLM để sinh **definition + example** cho đúng
những từ đó (LLM không tự chọn từ). Khi bank cạn, bot mới để LLM tự sinh từ mới
(fallback, giữ nguyên hành vi cũ).

Muốn mở rộng: thêm/sửa trực tiếp trong các file JSON đó, hoặc tạo file chủ đề mới —
format:
```json
[{"word": "mitigate", "part_of_speech": "verb"}]
```
Không cần điền definition/example, LLM sẽ tự sinh khi dùng đến.

## 7. Kiến trúc

```
bot/
  config.py           # đọc biến môi trường
  main.py             # entrypoint, load cogs, sync slash command, start scheduler
  scheduler.py         # APScheduler — daily job lúc 08:00
  db/
    models.py          # SQLAlchemy models (User, Vocabulary, DailyLesson, ...)
    session.py          # async engine/session
  llm/
    base.py             # LLMClient interface
    gemini_client.py     # implement Gemini
    ollama_client.py     # implement Ollama
    factory.py           # chọn provider theo LLM_PROVIDER
    prompts.py           # toàn bộ prompt templates
  services/
    word_bank.py          # đọc data/vocabulary/*.json
    vocabulary_service.py
    paraphrase_service.py
    writing_service.py
    quiz_service.py
    progress_service.py  # streak, spaced-repetition, weekly report
    lesson_service.py    # ghép các service trên thành 1 bài học/ngày
  cogs/
    daily.py, practice.py, writing.py, quiz.py, review.py, progress.py
```

## 8. Roadmap (v2 / v3, theo đề xuất ban đầu)

- v2: cải thiện spaced-repetition (SM-2 đầy đủ thay vì interval cố định), Personal Mistake Bank
  review riêng, thống kê theo ngày.
- v3: phân tích toàn bộ writing attempts của một user để tự sinh bài học nhắm đúng điểm yếu
  (personalized IELTS writing coach).
