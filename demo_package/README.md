# C5.1 데모 패키지 (대시보드 + PM앱 실시간 연동)

운영자 대시보드와 PM 작업자 앱을 **같은 origin**에서 함께 띄워, 둘 사이의
PM 작업 지시(요청/승인/보류/거절)가 **실시간 양방향**으로 연동되는 것을 보여줍니다.

## 구성
- `operator_dashboard.html` — 운영자 대시보드 (단일 파일)
- `pm_worker_app.html` — PM 작업자 앱 (단일 파일)
- `server.mjs` — 두 HTML을 한 origin에서 서빙하는 무의존성 정적 서버
- `start.bat` — Windows용 실행 런처 (더블클릭)

## 실행 방법

### Windows
1. `start.bat` 더블클릭
2. 브라우저에 두 탭이 자동으로 열립니다:
   - 대시보드: http://localhost:4173/
   - PM앱: http://localhost:4173/pm

### macOS / Linux / 수동 실행
```bash
node server.mjs
```
그 후 같은 브라우저의 두 탭에서 위 두 URL을 엽니다.

> **필수 조건**: Node.js (v16 이상)만 있으면 됩니다. 인터넷 연결 불필요
> (3D 모델의 Draco 디코더만 CDN을 사용하며, 오프라인이면 자동으로 2D로 폴백).

## 연동 테스트
1. 대시보드 → `긴급 PM 배차`로 작업 지시 발행 → PM앱에 "관제 요청"으로 즉시 표시
2. PM앱에서 승인/보류/거절 → 대시보드 `실시간 PM 작업 지시` 패널에 즉시 반영
3. 반대로 대시보드에서 결정해도 PM앱에 "관제 결정"으로 즉시 반영

## 주의
- **반드시 같은 브라우저**에서 두 URL을 여세요 (연동은 같은 origin의 탭/창 간에 동작).
- HTML 파일을 `file://`로 직접 열면 연동이 동작하지 않습니다 — 반드시 이 서버로 실행하세요.
- 포트 변경: `PORT=8080 node server.mjs`
- 자동 탭 열기 끄기: `NO_OPEN=1 node server.mjs`
- 연동 상태 초기화: 브라우저 개발자도구 콘솔에서 `localStorage.removeItem('c5_pm_orders_v1')` 실행 후 새로고침.
