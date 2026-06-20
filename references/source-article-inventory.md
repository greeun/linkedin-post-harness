# Source Article — Full Inventory

원문 "Harness Design for Long-Running Application Development"
(Prithvi Rajasekaran, Mar 24 2026, Anthropic engineering blog)의
전체 인벤토리. 하네스 운영이 원문에 충실하도록 보존한다.
도메인 매핑은 SKILL.md에, 여기서는 원문 사실만 기록한다.

---

## Publication
- Title: "Harness design for long-running application development"
- Author: Prithvi Rajasekaran (Anthropic Labs)
- Published: Mar 24, 2026

## Core problem
- Claude로 고품질 프론트엔드 디자인을 생성하는 것.
- Claude로 사람 개입 없이 완전한 애플리케이션을 구축하는 것.
- 프론트엔드 디자인 스킬과 장시간 코딩 에이전트 하네스에서 성능 한계에 도달.

## Key inspiration
- GAN(Generative Adversarial Networks)에서 영감.
- 핵심 설계: generator와 evaluator 에이전트로 구성된 멀티 에이전트 구조.
- 핵심 과제: 주관적 판단("이 디자인이 좋은가?")을 구체적·채점 가능한 기준으로 변환.

## Identified failure modes

### Context-related
- 컨텍스트 윈도우가 차면 모델이 일관성을 잃는다.
- **Context anxiety**: 컨텍스트 한계에 가까워졌다고 판단하면 작업을 조기 종결.
- 해법: **context resets** — 윈도우를 완전히 비우고 구조화 핸드오프로 새 에이전트 시작.
- **compaction과의 구분**: compaction은 연속성을 유지하나 깨끗한 시작을 주지 않는다;
  context anxiety는 compaction을 거쳐도 지속된다.
- 발견: Claude Sonnet 4.5에서 context anxiety가 심하여 compaction만으로 불충분.
- context resets은 오케스트레이션 복잡도·토큰 오버헤드·레이턴시를 추가한다.

### Self-evaluation
- 에이전트가 자기 작업을 자신 있게 칭찬, 품질이 보통이어도.
- 주관적 태스크(디자인 등)에서 특히 심각 — 이진 검증 불가.
- 해법: 작업하는 에이전트와 평가하는 에이전트를 **분리**.
- 독립 평가자를 회의적으로 튜닝하는 것이, generator를 자기비판적으로 만드는 것보다 용이.

## Frontend design harness

### 4 grading criteria
1. **Design quality** — 색상·타이포·레이아웃·이미지가 하나의 분위기와 정체성으로 읽히는가.
2. **Originality** — 템플릿·라이브러리 기본값·AI 패턴(gradient-over-card 등) 대신
   의도적이고 커스텀한 창작 결정이 보이는가.
3. **Craft** — 기술 실행: 타이포 위계, 간격 일관성, 색상 조화, 대비.
4. **Functionality** — 미학과 무관한 사용성: 인터페이스 이해, 주요 동작 발견, 추측 없이 완수.

### Weighting
- design quality와 originality를 craft·functionality보다 강조.
- Claude는 craft·functionality에서 기본적으로 높은 점수.
- 기준이 "AI slop" 패턴을 명시적으로 벌점 처리.
- "the best designs are museum quality" 같은 언어로 generator를 유도.

### Implementation
- Claude Agent SDK 기반.
- Generator: 사용자 프롬프트 기반 HTML/CSS/JS 프론트엔드 생성.
- Evaluator: Playwright MCP로 라이브 페이지 상호작용.
- Evaluator가 독립적으로 페이지를 탐색, 채점 전 스크린샷.
- **반복 횟수: 5–15회.**
- **벽시계 시간: 최대 4시간.**
- 매 평가 후 generator가 **전략적 결정**: 점수가 상승세면 다듬기, 아니면 **다른 미학으로 pivot**.
- Evaluator를 few-shot 예시(상세 점수 분석 포함)로 캘리브레이션.

### Key findings
- 반복에 따라 평가 점수 향상 후 plateau.
- **비선형**: 중간 이터레이션이 최종보다 선호될 수 있다.
- 라운드가 진행될수록 **구현 복잡도가 증가하는 경향**.

### Dutch Art Museum example
- 9라운드: 깔끔한 다크 테마 랜딩 페이지.
- **10라운드**: 접근을 **전면 폐기**, 3D 방(CSS perspective 체크 바닥), 자유 배치 작품,
  문 기반 갤러리 간 네비게이션으로 **재구상** — "단일 패스에서는 볼 수 없었던 창의적 도약".

## Full-stack coding harness — 3-agent architecture

### Planner
- 1–4문장의 단순 프롬프트를 받아 **전체 프로덕트 스펙으로 확장**.
- **스코프에 대해 야심차게** 지시.
- 제품 맥락과 상위 기술 설계에 집중, 상세 구현은 회피(cascading error 방지).
- AI 기능을 스펙에 엮으라고 지시.
- 프론트엔드 디자인 스킬에 접근 가능.

### Generator
- **한 번에 한 기능**(one-feature-at-a-time), 스프린트 단위 작업.
- 스택: React, Vite, FastAPI, SQLite (후에 PostgreSQL).
- 스프린트 끝에 자체 평가 후 QA에 핸드오프.
- git으로 버전 관리.

### Evaluator
- Playwright MCP로 사용자처럼 클릭하며 탐색.
- UI 기능, API 엔드포인트, DB 상태 테스트.
- 발견한 버그와 평가 기준으로 각 스프린트 채점.
- 기준: product depth, functionality, visual design, code quality.
- **각 기준에 hard threshold; 하나라도 실패하면 스프린트 실패.**
- 실패 원인에 대한 상세 피드백 제공.
- **Sprint contract negotiation**: generator와 evaluator가 코드 작성 전에
  "완료(done)" 의미에 합의. Generator가 빌드 내용과 검증 방법을 제안,
  evaluator가 올바른 것을 빌드하는지 검토. 합의까지 반복.
- **파일 기반 소통**: 에이전트 간 정보 전달은 파일 읽기/쓰기.

## Opus 4.5 implementation

### Context handling
- Opus 4.5가 context anxiety를 대부분 제거.
- 에이전트가 전체 빌드에 걸쳐 하나의 연속 세션으로 실행.
- Claude Agent SDK의 자동 compaction이 컨텍스트 증가 처리.

### RetroForge — solo vs harness

**Solo run**
- 소요: 20분, 비용: $9.
- 문제: 레이아웃 낭비, 경직된 워크플로우, 게임 고장(엔티티는 보이나 입력에 무반응),
  엔티티 정의↔런타임 연결 끊김(표면에 표시 없음).

**Full harness run**
- 소요: 6시간, 비용: $200 (solo 대비 20배 이상).
- Planner가 한 문장을 16-feature 스펙·10 스프린트로 확장.
- 추가 기능: 스프라이트 애니메이션, 행동 템플릿, 효과음, 음악,
  AI 스프라이트 생성, 레벨 디자이너, 공유 가능 게임 export.
- 장점: 더 나은 polish, 뷰포트 활용, 패널 크기, 시각 정체성 일관,
  풍부한 스프라이트 에디터, 깨끗한 팔레트, 더 나은 색상 피커·줌·Claude 통합,
  실제로 동작하는 게임(물리 엔진은 거칠지만 핵심 기능 작동).

### Evaluator 성능 이슈 & 튜닝
- 기본 상태에서 Claude는 **나쁜 QA 에이전트**.
- 합법적 문제를 발견한 뒤 **"별일 아니다"로 스스로 설득**.
- 엣지 케이스 대신 **피상적 테스트**.
- 튜닝 루프: evaluator 로그 → 판단 괴리 사례 → QA 프롬프트 업데이트.
- 평가 채점이 합리적이 되기까지 **개발 루프 수 라운드** 소요.
- 남은 한계: 작은 레이아웃 문제, 비직관적 상호작용, 중첩 기능의 미발견 버그.
- 추가 튜닝으로 검증 여유 확보 가능.

### Example contract failures

| 계약 기준 | 발견 |
|---|---|
| Rectangle fill: click-drag → 사각 영역 타일 채우기 | FAIL — 드래그 시작/끝 지점만 타일 배치. fillRectangle 함수는 존재하나 mouseUp에서 미호출. |
| Entity spawn points: 선택 후 삭제 | FAIL — delete 핸들러가 selection과 selectedEntityId 둘 다 필요하나, 클릭 시 selectedEntityId만 설정. |
| Animation frames: API로 순서 변경 | FAIL — PUT /frames/reorder 경로가 /{frame_id} 뒤에 정의되어 FastAPI가 "reorder"를 정수 frame_id로 매칭 → 422. |

## Harness iteration & simplification

### 핵심 원칙
- **하네스의 모든 구성요소는 "모델 혼자서는 할 수 없다"는 가정을 인코딩.**
  그 가정은 스트레스 테스트할 가치가 있다 — 처음부터 틀렸을 수도, 모델이 개선되며 낡았을 수도.

### 참조 원칙
- 작동하는 **가장 단순한 해법으로 시작**, 실제로 필요할 때만 복잡도 추가.

### 첫 단순화 시도
- 하네스를 **급진적으로 축소**.
- 창의적인 새 아이디어 시도.
- 원래 성능 재현 **불가**.
- 어떤 조각이 load-bearing인지 판별 곤란.
- **체계적 접근으로 전환: 한 번에 하나씩 제거.**

## Opus 4.6 release impact
- 하네스 복잡도를 줄일 추가 동기.
- 4.6은 4.5보다 적은 스캐폴딩이 필요할 것으로 기대.
- 4.6 특성: **더 신중한 계획, 더 긴 horizon 유지, 대규모 코드베이스에서 더 안정적 동작,
  더 강한 코드 리뷰·디버깅으로 자신의 실수를 더 많이 감지, long-context retrieval 대폭 개선.**
- 모두 하네스가 보완하려 만들어진 역량.

## Removing the sprint construct
- 업데이트된 하네스에서 **스프린트 구조를 완전히 제거**.
- 스프린트는 일관된 모델 실행을 위한 작업 분해에 도움이 되었음.
- Opus 4.6 개선이 모델이 분해 없이 작업을 처리할 수 있음을 시사.
- **Planner와 Evaluator는 유지** — 각각 명확한 가치를 계속 제공.
- Planner 없으면: generator가 **under-scoping하여 기능이 빈약한 앱** 생성.
- Evaluator를 매 스프린트가 아닌 **최종에 단일 패스**로 이동.
- **핵심 인사이트: evaluator 유용성은 태스크가 모델 기본 성능 대비 어디에 있는지에 달림.**
- 4.5에서 evaluator는 빌드 전반에서 의미 있는 이슈를 잡음(경계가 역량 가장자리).
- 4.6에서 기본 역량이 증가, 경계가 바깥으로 이동.
- 이전에 evaluator가 필요했던 태스크가 이제 native generator 역량 내.
- **역량 가장자리 태스크에서 evaluator는 여전히 실질적 리프트.**
- 함의: evaluator는 고정 yes/no가 아님 — **태스크가 안정적 단독 수행을 넘을 때 비용 대비 가치.**

## Prompting improvements
- 하네스가 앱에 AI 기능을 빌드하는 방식 개선을 위한 프롬프팅 추가.
- Generator가 도구를 통해 앱 기능을 구동하는 proper agent를 빌드하도록 집중.
- 최근 학습 데이터 커버리지가 얇아 **실질적 반복 필요**.
- 충분한 튜닝으로 generator가 에이전트를 올바르게 빌드.

## Updated harness (V2) results — DAW

프롬프트: "Build a fully featured DAW in the browser using the Web Audio API."

| Agent & phase | Duration | Cost |
|---|---|---|
| Planner | 4.7 min | $0.46 |
| Build (Round 1) | 2 hr 7 min | $71.08 |
| QA (Round 1) | 8.8 min | $3.24 |
| Build (Round 2) | 1 hr 2 min | $36.89 |
| QA (Round 2) | 6.8 min | $3.09 |
| Build (Round 3) | 10.9 min | $5.88 |
| QA (Round 3) | 9.6 min | $4.06 |
| **Total V2** | **3 hr 50 min** | **$124.70** |

### Output quality
- Builder가 스프린트 분해 없이 **2시간 이상 일관되게** 실행.
- Planner가 한 줄 프롬프트를 전체 스펙으로 확장.
- Generator가 앱과 에이전트 설계를 잘 계획, 에이전트를 연결, QA 핸드오프 전 테스트.
- R1 QA 피드백: 디자인 충실도·AI 에이전트·백엔드는 좋으나 핵심 DAW 기능이 display-only —
  클립 드래그/이동 불가, 악기 UI 패널 없음(synth knobs, drum pads),
  시각적 이펙트 에디터 없음(EQ curve, compressor meter).
- R2 QA 피드백: 오디오 녹음이 stub, 클립 리사이즈·분할 미구현,
  이펙트 시각화가 숫자 슬라이더(그래픽 EQ curve 아님).

### Achieved functionality
- 기능적 음악 제작 프로그램의 모든 핵심 조각 존재.
- 브라우저에서 동작하는 arrangement view, mixer, transport.
- 프롬프팅만으로 짧은 곡 스니펫 제작 가능.
- 에이전트가 템포·키 설정, 멜로디, 드럼 트랙, 믹서 레벨 조정, 리버브 추가.
- 프로 프로그램과는 거리가 있고, 에이전트의 작곡 능력에 개선 필요.
- Claude가 실제로 들을 수 없어 QA 피드백 루프가 음악적 취향 면에서 덜 효과적.

## Key learnings & future direction

### 일반 원칙
- 빌드 대상 모델로 **실험하는 것이 항상 좋은 관행**.
- 현실적 문제에서 **트레이스를 읽어라**.
- 원하는 결과를 달성하기 위해 **성능을 튜닝하라**.
- 복잡한 태스크: 분해하고 각 측면에 **전문 에이전트**를 적용.
- 새 모델 출시 시: 하네스를 **재검토**, 비하중 부품 제거, 더 큰 역량을 위한 새 부품 추가.

### 모델 개선에 대해
- 모델이 개선되면 더 긴 horizon, 더 복잡한 태스크 처리 가능.
- 경우에 따라 모델 주변 스캐폴드가 덜 중요해지며 문제가 새 모델 릴리스로 해결.
- 동시에, 강한 모델은 하네스가 raw model 단독 능력을 넘어 밀어붙일 여지를 더 열어줌.

### 저자의 확신
- 흥미로운 하네스 조합의 공간은 모델 개선에 따라 **축소되지 않는다 — 이동한다.**
- AI 엔지니어의 지속적 작업: 다음으로 유용한 조합을 계속 찾는 것.

## Acknowledgements
Mike Krieger, Michael Agaby, Justin Young, Jeremy Hadfield, David
Hershey, Julius Tarng, Xiaoyi Zhang, Barry Zhang, Orowa Sidker, Michael
Tingley, Ibrahim Madha, Martina Long, Canyon Robbins, Jake Eaton, Alyssa
Leonard, Stef Sequeira.
