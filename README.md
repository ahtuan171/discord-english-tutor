# English Vocabulary Bot — Discord Bot

Một bot Discord dạy từ vựng IELTS/academic mỗi ngày: **word → definition → example**,
kèm ôn tập theo spaced-repetition. **Không dùng LLM/AI** — toàn bộ nội dung lấy từ
database, phản hồi tức thì, không tốn API/thời gian chờ AI.

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
  Nếu dùng Supabase: lấy connection string ở nút **Connect → Session/Transaction pooler**
  (không dùng host `db.xxx.supabase.co` trực tiếp — host đó chỉ có IPv6, dễ không kết nối được).

## 3. Tạo bot & cấp quyền trên Discord Developer Portal

1. https://discord.com/developers/applications → **New Application**.
2. Tab **Bot** → **Reset Token** → copy vào `DISCORD_BOT_TOKEN`.
3. Vẫn ở tab **Bot**, bật **Privileged Gateway Intents**:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
4. Tab **OAuth2 → URL Generator**:
   - Scopes: ✅ `bot`, ✅ `applications.commands`
   - Bot Permissions: Send Messages, Send Messages in Threads, Embed Links, Read Message History, Add Reactions, Use Slash Commands
   - Copy URL sinh ra ở cuối trang → mở → chọn server → Authorize.

## 4. Chạy bot

```bash
python -m scripts.seed_dictionary   # chạy 1 lần: nạp dataset từ điển vào DB
python -m bot.main
```

Lần đầu chạy sẽ tự tạo bảng trong PostgreSQL. Slash command sẽ xuất hiện trong server ngay lập tức nếu bạn có set `GUILD_ID`.

### 4.1 Auto-start cùng Windows (Chạy ngầm liên tục)

Để bot **tự động khởi động ngay khi bật máy** và **chạy ngầm liên tục trong suốt quá trình mở máy** (không hiện cửa sổ cmd):

1. **Cài đặt autostart:** Double-click file `scripts/install_startup.bat` (hoặc chạy trong terminal).
   - Script sẽ tạo shortcut đăng ký bot khởi động cùng Windows.
2. **Chạy ngầm thử ngay lập tức:** Double-click file `scripts/run_hidden.vbs`.
3. **Kiểm tra log hoạt động:** Xem file `logs/bot.log` để kiểm tra trạng thái kết nối của bot.
4. **Hủy autostart (nếu không muốn tự chạy nữa):** Double-click file `scripts/uninstall_startup.bat`.

## 5. Lệnh có sẵn

| Command     | Mô tả                                                             |
|-------------|--------------------------------------------------------------------|
| `/vocab`    | Lấy 10 từ vựng **mới** (word + definition + example) — gọi nhiều lần/ngày đều ra từ khác nhau, không lặp; tự động thêm vào danh sách ôn tập |
| `/review`   | Ôn lại các từ đã học (kể cả vừa học qua `/vocab`, hoặc đang yếu) — nút I know / Almost / Don't know |
| `/quick`    | Streak Saver — ôn 3 từ yếu trong 1 phút khi bận                     |
| `/progress` / `/stats` | Weekly report: từ đã học, từ còn yếu, streak             |

Bot tự động đăng "Daily Drop" vào `DAILY_CHANNEL_ID` mỗi ngày lúc `DAILY_HOUR:DAILY_MINUTE`
(theo `TIMEZONE`), và sẽ không gửi trùng nếu bài học hôm đó đã tồn tại (kể cả khi bot restart nhiều lần).

## 6. Nguồn từ vựng — 100% từ database

Có 2 lớp dữ liệu, không lớp nào gọi AI:

1. **Word bank** (`data/vocabulary/*.json`) — **875 từ**, mỗi từ có definition + example
   **soạn thủ công** (không tra tự động), đúng nghĩa dùng trong IELTS writing/speaking band 7+:
   - 8 topic theo chủ đề IELTS (120 từ, file `01_...` đến `08_...`): environment, education,
     technology, health, economy, society_and_culture, crime_and_law, work_and_career.
   - 10 file `09_awl_sublist_1.json` đến `18_awl_sublist_10.json` (561 từ) — **toàn bộ**
     [Academic Word List](https://en.wikipedia.org/wiki/Academic_Word_List) của Coxhead
     (570 nhóm từ học thuật xuất hiện tần suất cao trong văn bản academic, công khai miễn
     phí cho giáo dục), xếp theo tần suất giảm dần (sublist 1 = tần suất cao nhất).
   - 2 file `19_common_vocabulary_1.json`, `20_common_vocabulary_2.json` (194 từ) — chọn từ
     [New General Service List](https://www.newgeneralservicelist.com) (CC BY-SA), lọc bỏ
     từ chức năng/quá cơ bản (the, a, is,...) và từ đã trùng với AWL/topic, giữ lại từ nội
     dung thông dụng hàng ngày (control, effect, decision, opportunity, evidence,...).

   Tên file có tiền tố số (`01_`, `02_`, ...) để cố định đúng thứ tự học — không dựa vào
   thứ tự alphabet (vì "awl..." sẽ đứng trước "environment..." nếu xếp theo chữ cái, phá vỡ
   trình tự 8 chủ đề IELTS trước, AWL sau như thiết kế). Đây quyết định **từ nào được dạy,
   theo thứ tự nào**. Ở nhịp 10 từ/lần `/vocab`, 875 từ đủ cho khoảng **88 lần** gọi lệnh
   không lặp — **mục tiêu 2000 từ đang làm dần theo từng batch** (đã chọn soạn thủ công
   thay vì tự động để giữ chất lượng, nên sẽ mở rộng tiếp qua nhiều lần trò chuyện sau).
2. **Dictionary dataset** (bảng `dictionary_entries` trong Postgres, seed từ
   [Wordset Dictionary](https://github.com/wordset/wordset-dictionary), CC-BY-SA 4.0) —
   chỉ dùng làm **fallback** cho từ mới bạn tự thêm vào word bank sau này mà không ghi
   definition/example thủ công. Với 875 từ hiện tại, bảng này không được dùng tới.

**Khi word bank cạn hết:** `/vocab` sẽ báo đã học hết, không lặp lại nội dung
cũ; bạn dùng `/review`/`/quick` để tiếp tục ôn các từ đã học theo spaced-repetition. Muốn
học tiếp từ mới thì thêm file JSON mới vào `data/vocabulary/` (đặt số thứ tự ≥ 19).

**Seed dictionary dataset (chạy 1 lần, hoặc sau khi đổi DB):**
```bash
python -m scripts.seed_dictionary
```
An toàn khi chạy lại nhiều lần (bỏ qua từ đã có). Script tải trực tiếp 27 file JSON từ
GitHub của Wordset — cần internet, không cần API key.

**Mở rộng word bank:** thêm/sửa trực tiếp trong các file JSON đó, hoặc tạo file chủ đề
mới, format:
```json
[{"word": "mitigate", "part_of_speech": "verb"}]
```
Không cần điền definition/example cho từ đơn — bot tự tra trong `dictionary_entries`.
Chỉ cần điền thủ công nếu từ đó là cụm nhiều từ / collocation.

> Ghi công: dữ liệu từ điển lấy từ [Wordset Dictionary](https://github.com/wordset/wordset-dictionary),
> giấy phép CC-BY-SA 4.0, xây dựng trên Princeton WordNet 3.0.

## 7. Kiến trúc

```
bot/
  config.py           # đọc biến môi trường
  main.py             # entrypoint, load cogs, sync slash command, start scheduler
  scheduler.py         # APScheduler — daily job lúc 08:00
  db/
    models.py          # SQLAlchemy models (User, Vocabulary, DictionaryEntry, UserVocabulary, DailyLesson)
    session.py          # async engine/session
  services/
    word_bank.py          # đọc data/vocabulary/*.json
    vocabulary_service.py  # chọn từ + tra dictionary_entries (không LLM)
    progress_service.py    # streak, spaced-repetition, weekly report
    lesson_service.py      # ghép thành 1 bài học/ngày
  cogs/
    daily.py, review.py, quick.py, progress.py
scripts/
  init_db.py            # tạo bảng
  seed_dictionary.py     # nạp dataset Wordset vào bảng dictionary_entries (chạy 1 lần)
data/
  vocabulary/*.json      # word bank theo chủ đề
```

## 8. Roadmap

- v2: cải thiện spaced-repetition (SM-2 đầy đủ), thêm chủ đề mới vào word bank.
- Tích hợp AI (paraphrase feedback, writing sample, chấm active-recall) đã được gỡ khỏi
  bot này theo yêu cầu — nếu muốn thêm lại sau, phần đó có thể làm một dịch vụ/bot riêng
  tách biệt khỏi phần từ vựng thuần database này.
