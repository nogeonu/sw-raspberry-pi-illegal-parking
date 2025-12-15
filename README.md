# CCTV 분석을 이용한 불법주정차 검거 프로젝트

## 📋 프로젝트 개요

한남대학교 스마트융합대학 소프트웨어 여름방학 캠프에서 진행한 프로젝트입니다.
라즈베리파이를 활용하여 Python으로 CCTV 영상을 분석하고 불법주정차 차량을 자동으로 검거하는 시스템을 구현했습니다.

## 🎯 프로젝트 목표

- YOLO 모델을 활용한 차량 번호판 실시간 탐지
- EasyOCR을 이용한 번호판 인식
- 불법주정차 시간 측정 및 데이터베이스 저장
- 라즈베리파이 환경에서의 실시간 영상 처리

## 🛠️ 기술 스택

- **Python 3.x**
- **YOLO (Ultralytics)** - 객체 탐지
- **EasyOCR** - 번호판 텍스트 인식
- **OpenCV** - 영상 처리
- **PyMySQL** - 데이터베이스 연동
- **Raspberry Pi** - 하드웨어 플랫폼

## 📁 프로젝트 구조

```
sw_불법주정차/
├── README.md
├── requirements.txt
├── sw_개발코드/
│   ├── yolo_n/
│   │   ├── parkiing_end.py      # 메인 실행 파일
│   │   ├── New_code.ipynb       # 개발 노트북
│   │   └── Nano_car_pt/         # 학습된 모델
│   └── yolo_m/
│       └── yolo_car/            # YOLO 모델 관련 파일
├── 원본 데이터/
│   ├── data.yaml                # 데이터셋 설정
│   ├── train/                   # 학습 데이터
│   ├── valid/                   # 검증 데이터
│   └── test/                    # 테스트 데이터
└── ppt/
    └── 불법주정차.pptx          # 프로젝트 발표 자료
```

## 🍓 라즈베리파이 환경 설정

### 라즈베리파이 소개

이 프로젝트는 **라즈베리파이 5 (Raspberry Pi 5, RPi5)**를 사용하여 구현되었습니다.

#### 라즈베리파이 5 주요 사양
- **프로세서**: BCM2712 (Quad-core Cortex-A76)
- **메모리**: 1GB, 2GB, 4GB 또는 8GB LPDDR4X-4267
- **무선 통신**: Dual-band 802.11ac Wi-Fi + Bluetooth 5.0
- **GPIO**: 40-pin GPIO 헤더
- **비디오 출력**: 2 x micro-HDMI
- **USB**: 2 x USB 3.0, 2 x USB 2.0
- **카메라**: 2 x MIPI CSI/DSI 커넥터
- **전원**: USB-C (5V, 5A 권장)

#### IoT Kit 구성품
- 라즈베리파이 5 보드
- 라즈베리파이 카메라 모듈
- DHT11 온습도 센서
- PMS7003 미세먼지 센서
- 브레드보드 및 점퍼선
- 기타 센서 및 모듈

### 라즈베리파이 5 설치

#### 1. Raspberry Pi OS 설치

1. **Raspberry Pi Imager 다운로드**
   - https://www.raspberrypi.com/software/
   - Raspberry Pi Imager를 다운로드하여 설치

2. **OS 이미지 작성**
   - SD 카드를 삽입
   - Imager에서 Raspberry Pi OS 선택
   - Hostname 설정: `RPi5-1`, `RPi5-2`, ... (각 라즈베리파이별로 구분)
   - SSH 활성화
   - 사용자 이름/비밀번호 설정: `admin` / `1234`
   - 무선 LAN 설정: `HNU_SW2024` / `12345678`
   - 이미지 작성 완료

3. **하드웨어 연결**
   - 전원 어댑터 연결 (USB-C)
   - 모니터 연결 (micro-HDMI)
   - 키보드, 마우스 연결

#### 2. 원격 접속 설정

**라즈베리파이에서 설정:**
```bash
sudo raspi-config
```

- **Interface Options > SSH**: Enable
- **Interface Options > VNC**: Enable

**PC에서 접속:**
- **SSH**: MobaXterm 사용
- **VNC**: RealVNC Viewer 사용

### 시스템 설정

#### 1. 시스템 정보 확인 및 업데이트

```bash
# Linux 커널 버전 확인 (6.6.31+)
uname -r

# 펌웨어 업데이트
sudo rpi-update
sudo reboot

# 패키지 최신 정보 업데이트
sudo apt update

# 최신 패키지 설치
sudo apt upgrade -y
```

#### 2. 한글 지원 설정

```bash
# 한글 폰트 설치
sudo apt install fonts-nanum -y
sudo apt install fonts-unfonts-core -y

# iBUS 설치
sudo apt install ibus -y
sudo apt install ibus-hangul -y

# 재부팅
sudo reboot
```

**GUI 설정:**
- Raspberry Pi Configuration > Localisation
- Language: `ko (Korean)`
- Character Set: `UTF-8`

#### 3. 필수 도구 설치

```bash
# Screen 설치 (백그라운드 실행용)
sudo apt install screen -y

# Java 설치
sudo apt install default-jdk -y

# VSCode 설치
sudo apt install code -y
```

#### 4. Miniconda 설치

```bash
# Miniconda 설치 디렉토리 생성
mkdir -p ~/miniconda3

# Miniconda 다운로드
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda3/miniconda.sh

# 설치 실행
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3

# 설치 파일 삭제
rm -rf ~/miniconda3/miniconda.sh

# 초기화
~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh

# 설정 적용
source ~/.bashrc

# base 환경 자동 활성화 비활성화
conda deactivate
conda config --set auto_activate_base false
```

#### 5. 웹 서버 설치

```bash
# Apache 웹 서버 설치
sudo apt-get install apache2 -y

# PHP 설치
sudo apt-get install php -y
sudo service apache2 restart

# MariaDB 설치
sudo apt-get install mariadb-server -y
```

#### 6. GPIO 라이브러리 설치

```bash
sudo apt install libgpiod2 -y
sudo apt remove python3-rpi-lgpio -y
sudo apt install python3-rpi.gpio -y
```

### Python 패키지 설치

#### 1. GPIO 및 센서용 가상환경

```bash
# 가상환경 생성
conda create -n dht11 python=3.9

# 가상환경 활성화
conda activate dht11

# GPIO 라이브러리 설치
pip install adafruit-blinka
pip install adafruit-circuitpython-dht
pip uninstall rpi-gpio
pip install rpi-lgpio

# MariaDB 연동
pip install pymysql

# 가상환경 비활성화
conda deactivate
```

#### 2. YOLOv8 영상 처리용 가상환경

```bash
# 가상환경 생성
conda create -n yolo python=3.9

# 가상환경 활성화
conda activate yolo

# OpenCV 설치 (라즈베리파이 5용)
# 참고: https://qengineering.eu/install%20opencv%20on%20raspberry%20pi%205.html
free -m  # 메모리 확인 (최소 5.8GB 필요)

# OpenCV 설치 스크립트 다운로드 및 실행
wget https://github.com/Qengineering/Install-OpenCV-Raspberry-Pi-64-bits/raw/main/OpenCV-4-10-0.sh
sudo chmod 755 ./OpenCV-4-10-0.sh
./OpenCV-4-10-0.sh

# YOLOv8 설치
sudo apt-get install python3-sympy -y
pip install ultralytics

# 가상환경 비활성화
conda deactivate
```

**참고**: YOLOv8 빠른 시작 가이드
- https://docs.ultralytics.com/ko/guides/raspberry-pi/

### 데이터베이스 설정

#### MariaDB 설정

```bash
# MariaDB root 접속
sudo mysql -u root -p
```

**데이터베이스 및 사용자 생성:**
```sql
-- 데이터베이스 생성
CREATE DATABASE db_sw2024 CHARACTER SET utf8 COLLATE utf8_general_ci;
SHOW DATABASES;

-- 사용자 생성
CREATE USER 'user_sw2024'@'%' IDENTIFIED BY 'sw2024';

-- 권한 부여
GRANT ALL PRIVILEGES ON *.* TO 'user_sw2024'@'%';
FLUSH PRIVILEGES;

-- 종료
EXIT;
```

**외부 접속 허용:**
```bash
# 설정 파일 수정
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

# bind-address = 127.0.0.1 주석 처리
# bind-address = 127.0.0.1  # 이 줄을 주석 처리

# MariaDB 재시작
sudo service mysql restart
```

**데이터베이스 정보:**
- Database name: `db_sw2024`
- User: `user_sw2024`
- Password: `sw2024`
- Host: `best.hnu.kr` (외부 서버) 또는 `localhost` (로컬)

### 센서 데이터 수집

#### 1. DHT11 온습도 센서

**GPIO 연결:**
- VCC → 3.3V
- GND → GND
- DATA → GPIO 6 (Pin 31)

**예제 코드:**
```python
import time
import board
import adafruit_dht
import pymysql

# 데이터베이스 연결
conn = pymysql.connect(
    host="best.hnu.kr",
    user="user_sw2024",
    passwd="sw2024",
    db="db_sw2024"
)

# 센서 설정
SENSOR_PIN = board.D6
sensor = 'DHT11'

try:
    with conn.cursor() as cur:
        sql = "INSERT INTO data_dht11(id, sensor, temp, humi) VALUES (%s, %s, %s, %s)"
        while True:
            try:
                mydht11 = adafruit_dht.DHT11(SENSOR_PIN, use_pulseio=False)
                humidity = mydht11.humidity
                temperature = mydht11.temperature
                
                if humidity is not None and temperature is not None:
                    print(f'Temp={temperature:.1f} Humidity={humidity:.1f}')
                    cur.execute(sql, (0, 'DHT11', temperature, humidity))
                    conn.commit()
                else:
                    print("Failed to get reading.")
            except RuntimeError as error:
                print(error.args[0])
            time.sleep(9)
except KeyboardInterrupt:
    print("Exit")
finally:
    conn.close()
```

**실행:**
```bash
conda activate dht11
python DHT11_temp_best.py
```

#### 2. PMS7003 미세먼지 센서

- **측정 범위**: 0.3~1.0μm (극초미세먼지), 1.0~2.5μm (초미세먼지), 2.5~10μm (미세먼지)
- **유효 범위**: 0 ~ 500
- **최대 범위**: > 1000

### 카메라 영상 처리

#### 라즈베리파이 카메라 설정

**카메라 소프트웨어 문서:**
- https://www.raspberrypi.com/documentation/computers/camera_software.html

**TCP 스트림 실행:**
```bash
# Screen 세션에서 실행
screen -S streem
rpicam-vid --width 1280 --height 720 -n -t 0 --inline --listen -o tcp://127.0.0.1:8888
```

**YOLOv8 실시간 탐지:**
```python
from ultralytics import YOLO
import pymysql

# 모델 로드
model = YOLO("yolov8s.pt")

# TCP 스트림에서 실시간 탐지
results = model("tcp://127.0.0.1:8888", stream=True, conf=0.5)

for result in results:
    boxes = result.boxes
    # 탐지 결과 처리 및 데이터베이스 저장
    result.save(filename="result.jpg")
```

### Telegram 연동

#### Telegram Bot 설정

1. **Bot Token 및 Chat ID 얻기**
   - https://gabrielkim.tistory.com/entry/Telegram-Bot-Token-%EB%B0%8F-Chat-Id-%EC%96%BB%EA%B8%B0

2. **Python 패키지 설치**
```bash
pip install pyTelegramBotAPI
```

3. **메시지 전송 예제**
```python
import telebot
from datetime import datetime

BOT_TOKEN = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'

bot = telebot.TeleBot(BOT_TOKEN)

# 텍스트 메시지 전송
msg_text = 'Raspi test'
bot.send_message(chat_id, msg_text)

# 이미지 전송
rpicam-jpeg --output test.jpg --timeout 2000 --width 640 --height 480
bot.send_photo(chat_id, open('test.jpg', 'rb'), caption=str(datetime.now())[:-7])
```

### 참고 자료

- **라즈베리파이 문서**: https://www.raspberrypi.com/documentation/
- **라즈베리파이 5 한글 입력기 설치**: https://blog.naver.com/mythee1/223300805398
- **PMS7003 프로토콜 예제**: https://github.com/eleparts/PMS7003
- **Telegram Bot 가이드**: https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/

## 🚀 설치 및 실행 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

`parkiing_end.py` 파일에서 데이터베이스 연결 정보를 수정하세요:

```python
conn = pymysql.connect(
    host="your_host",
    user="your_user",
    passwd="your_password",
    db="your_database",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
```

### 3. 모델 경로 설정

`parkiing_end.py` 파일의 20번째 줄에서 모델 경로를 수정하세요:

```python
model = YOLO('your_model_path/best.pt')
```

### 4. 실행

```bash
python sw_개발코드/yolo_n/parkiing_end.py
```

## 🔧 주요 기능

### 1. 실시간 번호판 탐지
- YOLO 모델을 사용하여 영상에서 차량 번호판을 실시간으로 탐지
- 신뢰도 임계값(0.6) 이상의 탐지만 인식

### 2. 번호판 인식
- EasyOCR을 사용하여 번호판 텍스트 추출
- 한국어 및 영어 지원
- 정규표현식을 통한 번호판 형식 검증 (예: "12가 3456")

### 3. 불법주정차 판단
- 차량이 30초 이상 정차: **불법주차**
- 차량이 30초 미만 정차: **불법정차**

### 4. 데이터 저장
- 탐지된 번호판 이미지 저장
- 데이터베이스에 다음 정보 저장:
  - 탐지 시간
  - 번호판 번호
  - 주정차 상태 (불법주차/불법정차)
  - 정차 시간

## 📊 데이터베이스 스키마

```sql
CREATE TABLE illegal_parking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datetime DATETIME,
    license_plate VARCHAR(20),
    parking_status VARCHAR(20),
    stopping_time VARCHAR(20)
);
```

## ⚙️ 설정 옵션

`parkiing_end.py` 파일에서 다음 설정을 변경할 수 있습니다:

- `CONFIDENCE_THRESHOLD`: 탐지 신뢰도 임계값 (기본값: 0.6)
- `CAP_PROP_FRAME_WIDTH`: 영상 너비 (기본값: 640)
- `CAP_PROP_FRAME_HEIGHT`: 영상 높이 (기본값: 480)
- 불법주차 판단 시간: 30초 (코드 127번째 줄)

## 📝 개발 과정

1. **데이터 수집 및 라벨링**: Roboflow를 사용하여 차량 번호판 데이터셋 구축
2. **모델 학습**: YOLOv8을 사용하여 번호판 탐지 모델 학습
3. **OCR 통합**: EasyOCR을 사용하여 번호판 텍스트 인식
4. **실시간 처리**: 라즈베리파이에서 실시간 영상 처리 구현
5. **데이터베이스 연동**: 탐지 결과를 데이터베이스에 저장

## 🎓 교육 내용

이 프로젝트는 다음 내용을 포함합니다:
- Python 프로그래밍
- 컴퓨터 비전 및 딥러닝
- YOLO 객체 탐지 모델
- OCR (광학 문자 인식)
- 데이터베이스 연동
- 라즈베리파이 활용

## 📄 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

## 👥 팀 멤버

이 프로젝트는 한남대학교 스마트융합대학 소프트웨어 여름방학 캠프에서 다음 팀원들이 함께 개발했습니다:

- **조철민**
- **노건우**
- **김서희**
- **박시현**
- **박종원**

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.

