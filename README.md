🚀 Superbases Tools

<p align="center">
  <strong>Production-Grade Supabase Backup, Migration & Recovery Toolkit</strong>
</p><p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-security">Security</a> •
  <a href="#-troubleshooting">Troubleshooting</a>
</p>---

📌 Overview

Superbases Tools adalah CLI toolkit untuk membantu mengelola backup, migration, restore, dan maintenance project Supabase melalui satu command-line interface yang sederhana.

Project ini dirancang untuk penggunaan di VPS / Linux server, dengan fokus pada:

- 🔐 Security
- ⚡ Simple CLI
- 🗄️ Reliable database backup
- ♻️ Safe restore workflow
- 📦 Storage migration
- 👤 Auth auditing
- ⚡ Edge Functions deployment
- 🧹 Backup retention
- 📣 Optional Telegram notification
- 🌍 Global command tanpa perlu masuk folder project

Setelah instalasi, Anda cukup menggunakan:

supamigrate

dari direktori mana pun.

---

✨ Features

Feature| Description
🗄️ Database Backup| Membuat backup PostgreSQL dari Supabase
♻️ Database Restore| Restore backup ke database target
🔎 Health Check| Memeriksa dependency, konfigurasi, dan koneksi database
📦 Storage Migration| Migrasi bucket dan object Supabase Storage
👤 Auth Report| Membuat laporan user Supabase Auth
⚡ Edge Functions| Deploy Edge Functions dari source lokal
🧹 Retention Policy| Membersihkan backup lama secara otomatis
📣 Telegram Notification| Notifikasi Telegram secara opsional
⏰ Scheduled Backup| Mendukung workflow backup menggunakan cron
🐳 Docker Support| Tersedia Dockerfile dan Docker Compose
🌍 Global CLI| "supamigrate" dapat dipanggil dari direktori mana pun
🔐 Environment Based Config| Credential disimpan di ".env", bukan source code

---

🧩 Architecture

                    ┌────────────────────────┐
                    │    SUPERBASES TOOLS    │
                    │       CLI / Python     │
                    └────────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │   SOURCE    │    │   BACKUPS   │    │   TARGET    │
       │   SUPABASE  │    │   ARCHIVES   │    │   SUPABASE  │
       └──────┬──────┘    └─────────────┘    └──────┬──────┘
              │                                      │
       ┌──────┼────────┐                      ┌──────┼────────┐
       │      │        │                      │      │        │
       ▼      ▼        ▼                      ▼      ▼        ▼
    Database Storage  Auth                 Restore Storage Functions

---

⚡ Quick Start

1. Clone Repository

git clone https://github.com/Cylne/Superbases-Tools.git
cd Superbases-Tools

2. Install

Jalankan:

chmod +x install.sh
sudo ./install.sh

Installer akan otomatis menyiapkan environment aplikasi.

Default installation directory:

/opt/Superbases-Tools

Virtual environment:

/opt/Superbases-Tools/.venv

Backup directory:

/opt/Superbases-Tools/backups

Configuration:

/opt/Superbases-Tools/config.json

Environment:

/opt/Superbases-Tools/.env

Global command:

/usr/local/bin/supamigrate

---

🌍 Global CLI

Salah satu tujuan utama Superbases Tools adalah membuat CLI yang mudah digunakan.

Setelah instalasi berhasil, Anda tidak perlu melakukan ini lagi:

cd /opt/Superbases-Tools
source .venv/bin/activate

Cukup:

supamigrate

Contoh:

cd /root

supamigrate check

Atau:

cd /home/user/project

supamigrate backup

Command tetap tersedia dari direktori mana pun.

---

🔐 Configuration

Superbases Tools menggunakan ".env" untuk menyimpan credential dan konfigurasi sensitif.

File utama:

/opt/Superbases-Tools/.env

Template tersedia di:

.env.example

Contoh:

SOURCE_DATABASE_URL=postgresql://...
TARGET_DATABASE_URL=postgresql://...

SOURCE_PROJECT_URL=https://YOUR_SOURCE_PROJECT.supabase.co
TARGET_PROJECT_URL=https://YOUR_TARGET_PROJECT.supabase.co

SOURCE_SERVICE_ROLE_KEY=
TARGET_SERVICE_ROLE_KEY=

SOURCE_PROJECT_REF=
TARGET_PROJECT_REF=

SUPABASE_ACCESS_TOKEN=

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

«⚠️ Jangan pernah memasukkan credential production ke GitHub.»

---

🧪 Verify Installation

Setelah konfigurasi selesai, jalankan:

supamigrate check

Command ini digunakan untuk memeriksa:

✓ Python environment
✓ PostgreSQL client
✓ psql
✓ pg_dump
✓ pg_restore
✓ Configuration
✓ Source database
✓ Target database
✓ Backup directory

Pastikan seluruh dependency dan koneksi yang diperlukan sudah benar sebelum melakukan migration atau restore.

---

🗄️ Database Backup

Untuk membuat backup:

supamigrate backup

Backup secara default disimpan di:

/opt/Superbases-Tools/backups

Untuk melihat opsi yang tersedia:

supamigrate backup --help

---

♻️ Database Restore

Restore backup menggunakan:

supamigrate restore /path/to/backup.archive

Contoh:

supamigrate restore /opt/Superbases-Tools/backups/database.archive

⚠️ Important

Restore merupakan operasi yang dapat mengubah database target.

Sebelum melakukan restore:

1. Pastikan file backup benar.
2. Pastikan target project benar.
3. Pastikan credential target benar.
4. Pastikan database target siap menerima restore.
5. Sebaiknya lakukan pengujian terlebih dahulu pada staging environment.

---

📦 Storage Migration

Untuk menjalankan migrasi Supabase Storage:

supamigrate storage

Fitur ini digunakan untuk workflow yang membutuhkan pemindahan:

Buckets
   ↓
Objects
   ↓
Target Storage

Lihat opsi:

supamigrate storage --help

---

👤 Auth Report

Untuk membuat laporan user Supabase Auth:

supamigrate auth-report

Fitur ini dapat digunakan untuk:

- Audit user
- Inventaris akun
- Dokumentasi project
- Pemeriksaan sebelum migration
- Verifikasi data setelah migration

«🔐 Auth report dapat berisi data sensitif. Simpan hasilnya di lokasi yang aman.»

---

⚡ Edge Functions

Untuk workflow Edge Functions:

supamigrate functions

Default directory:

supabase/functions

Lihat opsi:

supamigrate functions --help

---

🧹 Backup Retention

Superbases Tools mendukung retention policy untuk menjaga jumlah backup tetap terkendali.

Jalankan:

supamigrate retention

Default retention:

10 backup

Nilai tersebut dapat diubah melalui konfigurasi.

Contoh workflow:

Backup #01
Backup #02
Backup #03
...
Backup #10
       ↓
Retention
       ↓
Backup lama dibersihkan

---

📣 Telegram Notification

Telegram notification bersifat opsional.

Konfigurasi:

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

Jika dikonfigurasi, sistem dapat digunakan untuk workflow notifikasi backup atau operasi tertentu yang mendukung notification module.

---

⏰ Automated Backup

Script cron tersedia di:

scripts/install-cron.sh

Contoh workflow production:

             ┌──────────────┐
             │     CRON     │
             └──────┬───────┘
                    │
                    ▼
           supamigrate backup
                    │
                    ▼
             Backup Archive
                    │
                    ▼
            Retention Policy
                    │
                    ▼
           Telegram Notify

Sebelum mengaktifkan automated backup, selalu lakukan test manual:

supamigrate check
supamigrate backup

---

📁 Project Structure

Superbases-Tools/
│
├── supamigrate.py
│
├── modules/
│   ├── __init__.py
│   ├── auth.py
│   ├── backup.py
│   ├── checker.py
│   ├── config.py
│   ├── edge_functions.py
│   ├── notify.py
│   ├── restore.py
│   ├── retention.py
│   ├── storage.py
│   └── utils.py
│
├── scripts/
│   └── install-cron.sh
│
├── tests/
│   └── test_core.py
│
├── .env.example
├── .gitignore
├── config.example.json
├── Dockerfile
├── docker-compose.yml
├── install.sh
├── uninstall.sh
├── LICENSE
├── README.md
├── requirements.txt
└── requirements-dev.txt

---

⚙️ Configuration File

Template konfigurasi tersedia pada:

config.example.json

Struktur dasarnya:

{
  "source": {
    "name": "supabase-source",
    "database_url": "${SOURCE_DATABASE_URL}",
    "project_url": "${SOURCE_PROJECT_URL}",
    "service_role_key": "${SOURCE_SERVICE_ROLE_KEY}",
    "project_ref": "${SOURCE_PROJECT_REF:-}",
    "access_token": "${SUPABASE_ACCESS_TOKEN:-}"
  },
  "target": {
    "name": "supabase-target",
    "database_url": "${TARGET_DATABASE_URL}",
    "project_url": "${TARGET_PROJECT_URL}",
    "service_role_key": "${TARGET_SERVICE_ROLE_KEY}",
    "project_ref": "${TARGET_PROJECT_REF:-}",
    "access_token": "${SUPABASE_ACCESS_TOKEN:-}"
  }
}

File konfigurasi production:

/opt/Superbases-Tools/config.json

Credential tetap disimpan melalui environment variable.

---

🐳 Docker

Project menyediakan:

Dockerfile
docker-compose.yml

Docker dapat digunakan apabila Anda ingin menjalankan Superbases Tools dalam container-based environment.

Pastikan environment variable, volume backup, dan credential telah dikonfigurasi dengan benar sebelum menjalankan workflow production.

---

🧪 Development

Untuk development:

python3 -m venv .venv
source .venv/bin/activate

Install dependency:

pip install -r requirements-dev.txt

Jalankan test:

pytest

---

🔒 Security

Superbases Tools dapat menggunakan credential dengan akses tinggi terhadap Supabase.

Jangan lakukan

❌ Commit .env
❌ Commit config.json berisi credential
❌ Share service_role key
❌ Share database password
❌ Menaruh password di source code
❌ Upload backup database ke repository public
❌ Menjalankan restore tanpa memeriksa target

Disarankan

✅ Gunakan environment variables
✅ Gunakan repository private jika diperlukan
✅ Batasi akses VPS
✅ Gunakan SSH key
✅ Simpan backup pada storage yang aman
✅ Test restore secara berkala
✅ Monitor automated backup
✅ Rotate credential jika terjadi kebocoran

---

🔄 Recommended Production Workflow

Workflow yang direkomendasikan:

┌──────────────────────┐
│  Configure .env      │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  supamigrate check   │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Create Backup       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Verify Backup        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Migration / Restore  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Verify Target        │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Apply Retention      │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Scheduled Backup     │
└──────────────────────┘

Untuk database production, lakukan pengujian pada staging environment terlebih dahulu apabila memungkinkan.

---

🆘 Troubleshooting

"supamigrate: command not found"

Periksa instalasi:

sudo ./install.sh

Kemudian:

command -v supamigrate

Expected:

/usr/local/bin/supamigrate

---

Database host tidak ditemukan

Jika muncul:

could not translate host name

periksa:

SOURCE_DATABASE_URL=
TARGET_DATABASE_URL=

Pastikan connection string menggunakan host Supabase yang sebenarnya.

Jangan menggunakan placeholder seperti:

aws-0-REGION.pooler.supabase.com

---

Configuration not found

Periksa:

ls -la /opt/Superbases-Tools/.env
ls -la /opt/Superbases-Tools/config.json

Kemudian:

supamigrate check

---

PostgreSQL command tidak tersedia

Periksa:

which psql
which pg_dump
which pg_restore

Kemudian:

supamigrate check

Jika dependency belum tersedia, jalankan installer kembali:

sudo ./install.sh

---

🗑️ Uninstall

Untuk menghapus instalasi:

sudo /opt/Superbases-Tools/uninstall.sh

Sebelum uninstall, pastikan backup penting telah dipindahkan ke lokasi penyimpanan lain.

---

📜 License

Project ini menggunakan license yang tersedia pada:

LICENSE

Silakan baca file tersebut untuk informasi lengkap mengenai penggunaan dan distribusi project.

---

👨‍💻 Author

Cylne

GitHub:

https://github.com/Cylne

Repository:

https://github.com/Cylne/Superbases-Tools

---

<p align="center">
  <strong>🚀 Superbases Tools</strong>
  <br>
  Production-ready Supabase backup, migration & recovery workflow.
  <br><br>
  <sub>Built with ❤️ for reliable infrastructure management.</sub>
</p>