# dstoolbox-gprj

โปรเจกต์นี้เป็นงานกลุ่มที่พัฒนาระบบวิเคราะห์ข้อมูลสมาร์টโฟน ด้วย Django และ Matplotlib

---

## วิธีการติดตั้งและใช้งาน

### 1. Clone Repository
```bash
git clone https://github.com/ManYaiMark/dstoolbox-gprj.git
cd dstoolbox-gprj
git checkout project  # ถ้า branch ต่างจาก main
```

### 2. สร้าง Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 4. ตั้งค่า Environment Variables
สร้างไฟล์ `.env` ที่ root folder (เดียวกับ manage.py):

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

**วิธีสร้าง SECRET_KEY:**
```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
exit()
```

### 5. รันการ Migrate
```bash
python manage.py migrate
```

### 6. สร้าง Superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. รัน Development Server
```bash
python manage.py runserver
```

ไปที่ `http://127.0.0.1:8000/` ในเบราว์เซอร์

---

## หมายเหตุสำคัญ

### ไฟล์ที่ถูกลบออก
- `db.sqlite3` - ลบออกจากการ track ใน git เพื่อหลีกเลี่ยง conflict

**หากเป็นคนใหม่ที่ clone:** 
- ไฟล์นี้จะไม่มีใน repository
- Django จะสร้างอันใหม่เองเมื่อรัน migrate
- นี่เป็นพฤติกรรมปกติและปลอดภัย

### ข้อมูลสำคัญที่ย้ายไปไว้ใน .env
- `SECRET_KEY` - เก็บใน `.env` แทนที่จะ hardcode
- ไฟล์ `.env` **ไม่ได้ commit ขึ้น git** เพื่อความปลอดภัย

**วิธีใช้:**
1. ใน `.env` เก็บค่าที่ไม่ต้องการให้คนอื่นเห็น
2. ใน `settings.py` ดึงค่าจาก environment:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   SECRET_KEY = os.getenv('SECRET_KEY')
   ```

---

## การแก้ไขเก็บในรอบนี้

### Security Fixes
- เปลี่ยน `role` registration ให้ default เป็น 'member' (ไม่ให้ user self-assign role)
- เพิ่ม CSRF token ในฟอร์ม
- ย้าย SECRET_KEY ไป .env file
- ตั้ง DEBUG = False สำหรับ production

### Bug Fixes
- ลบ duplicate `groups` และ `user_permissions` fields
- ตรวจสอบว่า dashboard chart ไม่ crash เมื่อไม่มี data

### Feature Improvements
- แก้ระบบคะแนน (points system)
- แก้ระบบคูปอง (coupon system)
- Filter order ให้แสดงแค่ของผู้ใช้ที่เข้าสู่ระบบ

### Code Quality
- ลบไฟล์ที่ไม่ใช้งาน
- ปรับปรุง import statements
- เพิ่ม error handling

---

## โครงสร้างโปรเจกต์

```
dstoolbox-gprj/
├── manage.py
├── requirements.txt
├── .env.example          # Template สำหรับ .env
├── .gitignore           # ห้าม commit: .env, db.sqlite3, __pycache__
├── dsproject/
│   ├── settings.py      # ใช้ environment variables
│   ├── urls.py
│   └── ...
├── matplotlibapp/
│   ├── views.py         # Views สำหรับ chart generation
│   ├── models.py
│   ├── tests.py         # Unit tests
│   └── ...
└── media/
    └── smartphones_cleaned_v6.csv
```

---

## Tips for Development

- ไม่ต้องเพิ่ม `db.sqlite3` ขึ้น git
- ตรวจสอบว่า `.env` อยู่ใน `.gitignore`
- เมื่อ clone ใหม่ให้สร้าง `.env` เอง
- ใช้ `python manage.py test` เพื่อรัน unit tests

---

## ติดต่อหรือปัญหา

หากมีคำถามสามารถเปิด issue ใน GitHub repository นี้

---

**Last Updated:** 2024
