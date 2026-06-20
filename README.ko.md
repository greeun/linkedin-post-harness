# LinkedIn Post Harness

Anthropic의 [Harness Design for Long-Running Application Development](https://www.anthropic.com/engineering/harness-design-long-running-apps) (Prithvi Rajasekaran, 2026) 방법론을 LinkedIn 글쓰기에 이식한 Claude Code 스킬입니다. **Planner → Generator → Evaluator** 3-역할 하네스로 포스트를 작성하고, 루브릭 평가 통과 후 LinkedIn API로 실제 게시합니다.

## 왜 하네스인가?

단일 패스 AI 글쓰기는 클리셰 투성이의 평범한 결과를 냅니다. 이 스킬은 Anthropic 원문의 핵심 아이디어인 **"작성하는 에이전트와 평가하는 에이전트의 분리"**(GAN 영감)를 적용하여, 루브릭 기반 라운드를 반복하며 품질 임계값을 넘길 때까지 다듬습니다 — Anthropic의 프론트엔드 디자인 실험에서 "창의적 도약"을 만들어낸 바로 그 아키텍처입니다.

## 동작 방식

```
사용자: "링크드인 글 작성해줘"
         |
    [Planner] ─── spec.md + 스프린트 계약 ──→ 사용자 승인
         |
    [Generator] ── post_v1.md + handoff.md
         |
    [Evaluator] ── critique.md (4기준, 각 1-5점)
         |          실패 → Generator 재작성 (최대 3회)
         |          통과 → 다음 라운드
         |
     ... R1 → R2 → R3 ...
         |
    final_post.md 확정
         |
    ★ 사용자에게 전문 출력 → 명시적 승인 필수 ★
         |
    LinkedIn API로 게시
```

## 핵심 원칙 (원문 이식)

| 원문 개념 | LinkedIn 매핑 |
|---|---|
| GAN식 generator/evaluator 분리 | Draft-writer와 비평가 역할을 명시적으로 분리 |
| Context anxiety (조기 종결 편향) | "충분히 길어 보인다"로 드래프트를 닫지 말 것 — 루브릭 통과만이 종료 조건 |
| Context reset + 구조화 핸드오프 | 매 라운드 말미에 `handoff.md` 작성, 다음 라운드는 새 컨텍스트 |
| Sprint contract negotiation | Planner와 Generator가 "완성" 기준을 사전 합의 |
| 자기평가 편향 | Generator는 **절대** 자기 채점 금지 — 오직 Evaluator만 채점 |
| 전략적 pivot | 점수 정체 시 관점·어조·구조를 전면 전환 |
| Evaluator 자기설득 방지 | "문제 발견 → 별일 아니라고 자기 설득" 패턴 탐지 시 루브릭 강화 |
| 가장 단순한 해법 우선 | 단순 공지는 단일 패스, 씬 리더십은 다중 라운드 |
| V1→V2 진화 | 모델 개선으로 스프린트 제거 가능, 그러나 Planner·Evaluator는 유지 |

원문의 전체 인벤토리(예시·수치·사례)는 [`references/source-article-inventory.md`](references/source-article-inventory.md)에 보존.

## 평가 기준 (각 1-5, 통과 = 전 기준 >= 4)

1. **Strategic coherence** — 훅 → 주장 → 근거 → CTA가 한 덩어리로 읽히는가
2. **Originality & insight** — 이 주제에 고유한 비자명 관점. 클리셰·AI 슬롭 감점
3. **Craft** — 문장 밀도, 줄바꿈 리듬, 서식, 어조 일관성, 오탈자
4. **Action clarity** — 독자가 다음 행동을 모호함 없이 안다

**가중치:** Strategic coherence와 Originality가 Craft·Action clarity보다 상위 (원문의 design quality/originality 우선과 동일).

## 설정

### 1. 환경 변수

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export LINKEDIN_ACCESS_TOKEN="your-oauth2-access-token"
export LINKEDIN_AUTHOR_URN="urn:li:person:your-member-id"
# 회사 페이지인 경우:
# export LINKEDIN_AUTHOR_URN="urn:li:organization:your-org-id"
```

### 2. LinkedIn Access Token 발급

1. [LinkedIn Developer Portal](https://www.linkedin.com/developers/)에서 앱 생성
2. **Share on LinkedIn** (또는 **Marketing Developer Platform**) 제품 추가
3. OAuth 2.0 Authorization Code Flow로 `w_member_social` scope 토큰 발급
4. `/v2/userinfo` 호출하여 member ID 확인 → URN 구성

### 3. 설치

`linkedin-post-harness/` 폴더를 `~/.claude/skills/`에 복사합니다.

## 사용법

### 트리거 문구

Claude Code에서 아래처럼 말하면 자동 실행됩니다:

- "링크드인 글 작성해줘"
- "링크드인에 올릴 포스트 써줘"
- "링크드인 채용글 만들어줘"
- "LinkedIn thought leadership on..."

### 게시 스크립트

```bash
# 텍스트 포스트
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md

# 링크 프리뷰 포함
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --link "https://example.com" --link-title "제목"

# 이미지 첨부
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --image ./cover.png --image-alt "이미지 설명"

# 드라이런 (게시 없이 payload만 확인)
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md --dry-run
```

기본적으로 `"yes"` 타이핑 확인을 요구합니다. 채팅에서 이미 승인받았다면 `--yes` 플래그로 스킵 가능.

### 스크립트 옵션

| 옵션 | 설명 | 필수 |
|---|---|---|
| `--text` / `--text-file` | 포스트 본문 (인라인 또는 파일 경로) | O (택 1) |
| `--visibility` | `PUBLIC` (기본) 또는 `CONNECTIONS` | X |
| `--link` | 링크 프리뷰용 URL | X |
| `--link-title` | 프리뷰 제목 | X |
| `--link-description` | 프리뷰 설명 | X |
| `--image` | 로컬 이미지 경로 (업로드) | X |
| `--image-alt` | 이미지 대체 텍스트 | X |
| `--dry-run` | 게시 없이 payload만 출력 | X |
| `--yes` | 대화형 확인 스킵 | X |

## 산출물

모든 아티팩트는 `linkedin-post/` 디렉토리에 생성됩니다:

| 파일 | 내용 |
|---|---|
| `spec.md` | Planner의 스펙 및 스프린트 계약 |
| `post_v1.md` ... `post_vN.md` | 라운드별 드래프트 |
| `critique_v1.md` ... | Evaluator 채점 및 피드백 |
| `handoff.md` | 라운드 간 핸드오프 메모 |
| `final_post.md` | 승인된 최종 포스트 |
| `publish_log.md` | 게시 후 URN·시각·게시자 기록 |

## 안전 장치

- **필수 사용자 승인**: 모든 평가 라운드를 통과해도 사용자 명시 승인 없이는 절대 게시하지 않음
- **대화형 확인**: 게시 스크립트가 API 호출 전 `"yes"` 입력을 요구
- **드라이런**: `--dry-run`으로 언제든 payload 사전 확인 가능
- **3,000자 제한**: Evaluator와 스크립트 양쪽에서 강제

## 프로젝트 구조

```
linkedin-post-harness/
├── SKILL.md                              # 하네스 지시문
├── README.md                             # English README
├── README.ko.md                          # 이 파일
├── scripts/
│   └── publish_linkedin.py               # LinkedIn UGC Posts API 게시 스크립트
└── references/
    ├── source-article-inventory.md       # 원문 전체 인벤토리 (보존)
    ├── post-patterns.md                  # 훅 패턴, 템플릿, AI 슬롭 체크리스트
    └── linkedin-api.md                   # API 주의사항 및 Rate limit
```

## 크레딧

방법론 출처:
- **"Harness Design for Long-Running Application Development"** by Prithvi Rajasekaran, Anthropic (Mar 2026)
- Planner → Generator → Evaluator 3-에이전트 아키텍처, 스프린트 계약, 컨텍스트 리셋, 루브릭 평가, 자기평가 편향 방지를 LinkedIn 포스트 작성 도메인에 적용.

## 라이선스

MIT
