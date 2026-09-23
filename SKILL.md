---
name: linkedin-post-harness
description: |
  LinkedIn 포스트를 Planner → Generator → Evaluator 하네스로 작성·게시.
  Anthropic "Harness Design for Long-Running Application Development" (Prithvi Rajasekaran, 2026)의
  원칙(역할 분리·컨텍스트 리셋·스프린트 계약·루브릭 평가·컨텍스트 불안 방지·자기평가 편향 방지)을
  LinkedIn 글쓰기 도메인에 이식한다. 평가 통과 시 LinkedIn UGC Posts API로 실제 게시.

  트리거 — EN: "LinkedIn post", "post to LinkedIn", "write a LinkedIn post",
  "publish on LinkedIn", "share on LinkedIn", "LinkedIn article",
  "LinkedIn thought leadership", "LinkedIn announcement".
  KO: "링크드인 글", "링크드인 포스트", "링크드인에 올려", "링크드인 게시",
  "링크드인 공유", "링크드인 작성", "링크드인 글 작성", "링크드인 글 올리기",
  "링크드인 홍보", "링크드인 채용글", "링크드인 발표글", "링크드인 아티클".
version: 1.0.0
---

# LinkedIn Post Harness

LinkedIn용 장문·단문 포스트를 3-역할 하네스(Planner → Generator → Evaluator)로
생성하고, 평가 통과 시 LinkedIn API로 실제 게시한다.

방법론은 Anthropic의 "Harness Design for Long-Running Application Development"
(Prithvi Rajasekaran, 2026) 원문 원칙의 직역 이식이다. 원문의 핵심 원칙은
아래 **Source Principles** 섹션에 보존한다.

---

## Input

사용자가 제공하지 않았다면 다음만 물어본다:

> **주제(Topic):** 한 단락 분량의 포스트 주제·청중·목적(인지·전환·채용·발표 등)과
> 알려진 제약(업종, 톤, 필수 포함 문구, 금칙어, 길이 목표, 링크/이미지).

답변을 `{{LINKEDIN_TOPIC}}`로 저장하고 진행한다.

---

## Source Principles (원문 직역 이식)

이 스킬은 아래 원칙을 그대로 따른다. 코드 하네스의 개념을 글쓰기 도메인에 매핑한다.

| 원문 개념 | LinkedIn 포스트 하네스 매핑 |
|---|---|
| GAN식 generator/evaluator 분리 | Draft-writer와 비평가 역할 명시적 분리 |
| Context anxiety (조기 종결 편향) | "충분히 길어 보인다"는 이유로 드래프트를 조기에 닫지 말 것 — 루브릭 통과 기준으로만 종료 |
| Context reset + 구조화 핸드오프 | 각 라운드 말미에 `handoff.md` 작성, 다음 라운드는 새 컨텍스트에서 그 파일만 읽고 시작 |
| Compaction과의 구분 | 조용한 요약 금지 — 반드시 명시적 handoff 파일 작성 |
| Sprint contract negotiation | Planner와 Generator가 "완성(done)" 기준을 드래프트 전에 문서로 합의 |
| Design quality | Strategic coherence — 훅·주장·증거·CTA가 한 덩어리로 읽히는가 |
| Originality | Non-obvious insight — 템플릿·클리셰·AI 티 나는 문장 배제. 이 주제에 고유한 관점 |
| Craft | 문장 밀도·리듬·서식(줄바꿈·불릿)·어조 일관성·오탈자 |
| Functionality | Action clarity — 독자가 다음에 뭘 할지 즉시 안다 |
| Playwright MCP 프로빙 | Evaluator가 정량 근거·링크·인용·수치를 실제로 확인(의심 시 WebFetch) |
| 5–15 iteration | 1–5라운드 내 수렴을 목표, 최대 5라운드 |
| "simplest solution first" | 루브릭·라운드는 과제에 필요한 만큼만 — 단순 공지는 1라운드로 축약 |
| "every component encodes an assumption" | 라운드 중 가정이 틀렸다고 판단되면 Planner가 계약을 재협상(문서화) |
| Evaluator tuning loop | 비평가가 관대하다고 판단되면 루브릭 하드 스레숄드를 강화 |
| 자기평가 편향 | Generator는 **절대** 자기 채점 금지 — 평가는 오직 Evaluator |
| Generator 전략적 pivot | 매 평가 후 Generator가 전략적 결정: 점수 상승세면 다듬기, 아니면 **관점·어조·구조를 전면 전환**(Dutch Museum 예시: 9라운드 랜딩→10라운드에서 전체 재구상 — 단일 패스에서는 나오지 않는 창의적 도약) |
| Evaluator few-shot 캘리브레이션 | Evaluator를 상세 점수 분석이 포함된 few-shot 예시로 교정. 아래 Evaluator 역할의 **캘리브레이션 지침** 참조 |
| 비선형 반복 발견 | 중간 라운드 드래프트가 최종보다 나을 수 있다 — 라운드 간 "가장 좋았던 버전"을 `handoff.md`에 기록. 복잡도가 라운드마다 늘어나는 경향에 주의 |
| Evaluator 자기설득 구체 패턴 | 원문: "합법적 문제를 발견한 뒤 '별일 아니다'로 스스로 설득, 엣지 케이스 대신 피상적 테스트." 이 패턴을 탐지하면 루브릭 강화 |
| Planner 없으면 under-scoping | Planner를 건너뛰면 Generator가 스코프를 줄여 빈약한 포스트를 생성. Planner가 야심 차고 구체적인 spec을 만들어야 품질이 오른다 |
| Evaluator 유용성 = 태스크 경계 | Evaluator는 고정 yes/no가 아님. 모델 기본 역량 경계 근처 태스크에서만 실질적 리프트. 단순 공지처럼 경계 안쪽이면 단일 패스로 축약, 씬 리더십처럼 경계 바깥이면 다중 라운드 필수 |
| V1→V2 진화 | V1(스프린트 기반·매회 평가) → V2(스프린트 제거·최종 평가). 이유: 모델 개선으로 분해 없이도 일관된 장시간 실행 가능. 그러나 Planner·Evaluator는 각각 명확한 가치를 계속 제공하므로 유지 |
| 급진적 단순화 실패 교훈 | 하네스를 한꺼번에 줄이면 성능 재현 불가. **한 번에 하나씩 제거**해야 load-bearing 부품 식별 가능 |
| 하네스 공간은 축소가 아닌 이동 | 모델 개선에 따라 하네스 조합의 공간은 줄어들지 않고 이동한다. 비하중 부품은 제거하되, 더 큰 역량을 위한 새 부품을 추가하라 |

원문의 전체 인벤토리(예시·수치·사례 포함)는
[references/source-article-inventory.md](references/source-article-inventory.md)에 보존.

---

## Roles

### Planner
- Input: `{{LINKEDIN_TOPIC}}`, 사용자 제약.
- Output: `spec.md` — 목표(목적·성공지표), 청중(페르소나·현업 맥락),
  핵심 메시지(주장 1개), 근거/데이터 포스트(있다면), 톤·보이스, 포맷
  (단문 ≤300자 / 중문 300–1,300자 / 장문 1,300–3,000자 — LinkedIn 상한 3,000자),
  훅 후보 3개, CTA, 해시태그 3–5개, 금칙·필수 문구, 이미지/링크 첨부 여부,
  **Sprint Contract**(각 라운드의 acceptance criteria).
- 이 주제에 고유한 "insight hook"을 반드시 1개 포함(코드 하네스의 "weave AI features"에 해당).
- 모호함은 `spec.md`에 명시적으로 해소.

### Generator
- Input: `spec.md` + 현재 Sprint Contract + 직전 라운드의 `critique.md`.
- Output: `post_vN.md`(드래프트) + `handoff.md`(무엇을 썼고, 어떤 가정을 했고,
  다음 라운드가 무엇을 고쳐야 하는지, 그리고 **지금까지 가장 좋았던 버전 번호**).
- **자기 채점 금지.** 오직 계약 이행.
- **전략적 pivot 판단**: 매 평가 후, 점수가 상승세면 현재 방향을 다듬는다. 정체거나
  하락이면 관점·어조·구조를 **전면 전환**한다(원문 Dutch Museum 사례: 9라운드의 다크 랜딩을
  10라운드에서 완전히 다른 공간 경험으로 재구상 — 단일 패스에서는 나오지 않는 창의적 도약).
- 파일로만 소통(대화형 요약 금지).
- 복잡도 증가 경계: 라운드가 거듭될수록 문장·구조가 불필요하게 복잡해지는 경향에 주의.

### Evaluator
- Input: `spec.md`, 계약, `post_vN.md`.
- Output: `critique.md` — 각 기준 1–5 점수 + 줄 단위 지적 + 수정 지시.
- 적극적 프로빙: 수치·인용·링크는 실제 검증(의심 시 WebFetch). 훅을 소리 내어 읽었을 때
  스크롤을 멈출지 판단. 클리셰·AI 슬롭·이모지 과용·따옴표 남용을 벌점 처리.
- **자기 설득 금지:** 원문의 구체 실패 패턴 — "합법적 문제를 발견한 뒤 '별일 아니다'로
  스스로 설득, 엣지 케이스 대신 피상적 테스트" — 이 패턴이 감지되면 루브릭 하드 스레숄드를
  강화한다. 사소한 문제라도 반드시 기록. 실패 기준에 해당하면 반려.
- **캘리브레이션 지침**: 첫 라운드 전, 아래 형식의 few-shot 점수 분석을 내부적으로 구성하여
  채점 기준선을 잡는다: "Strategic coherence 4 — 훅→주장은 연결되나 CTA와의 논리적 연결이
  약함", "Originality 2 — '바쁜 세상에서…' 류 오프닝, 고유 관점 부재" 등. 라운드가 진행되며
  채점이 관대하다고 판단되면 기준선을 상향.
- 통과 기준: 모든 기준 ≥4 AND 어떤 기준도 unresolved blocker 없음.

---

## Grading Criteria (1–5, 매 라운드 적용)

1. **Strategic coherence** — 훅 → 주장 → 근거 → CTA가 한 덩어리로 읽히는가.
2. **Originality & insight** — 이 주제에 고유한 비자명한 관점이 있는가.
   템플릿/클리셰/AI 티 문장("In today's fast-paced world...") 감점.
3. **Craft** — 문장 밀도, 줄바꿈 리듬, 서식, 어조 일관성, 오탈자.
   LinkedIn 읽기 패턴(모바일 3–4줄 단락, 첫 2줄이 "see more" 이전에 훅) 충족.
4. **Action clarity** — 독자가 다음 행동(저장·댓글·DM·링크 클릭·지원 등)을
   모호함 없이 안다.

**Weighting:** Strategic coherence와 Originality를 Craft·Action clarity보다
상위에 둔다(원문의 design quality/originality 우선 가중치와 동일).
통과: 전 기준 ≥4 AND 모든 blocker 해결.

**Hard fail triggers** (즉시 반려):
- 3,000자 초과 / 해시태그 0개 또는 10개 초과
- 훅이 첫 2줄 이후 등장
- 검증 불가능한 수치 인용
- CTA 부재(단, Planner가 명시적으로 "CTA 없음"으로 계약한 경우 제외)

---

## Default Round Sequence (Planner가 조정 가능)

1. **R1 Hook & Thesis** — 훅 3안 + 주장 1문장 + 구조 개요.
2. **R2 Body** — 근거·예시·데이터로 주장 뒷받침. 클리셰 제거.
3. **R3 Polish** — 서식·리듬·CTA·해시태그·플랫폼 적합성 최종 다듬기.
4. **(옵션) R4 Revision** — Evaluator가 지적한 잔여 blocker 수정.

주제가 좁고 사용자가 opt-in하면 단일 패스(최종에만 Evaluator)로 축약한다
(원문 Opus 4.6 단순화에 해당).

---

## Execution Protocol

1. `{{LINKEDIN_TOPIC}}`을 한 문장으로 사용자에게 재확인.
2. 작업 디렉토리 `linkedin-post/` 를 현재 경로(또는 사용자 지정 경로)에 생성.
3. **Planner** 실행 → `spec.md` + Sprint Contract 작성 후 **정지**, 사용자 go 대기.
4. 각 라운드:
   a. Generator가 `post_vN.md` + `handoff.md` 작성.
   b. Evaluator가 `critique.md` 작성(점수 + 지적).
   c. 실패 시 Generator 재작성(라운드당 최대 3회 리비전).
      여전히 실패면 Planner가 계약을 문서로 재협상.
   d. 통과 시 `handoff.md`를 핸드오프 삼아 **컨텍스트 리셋** 후 다음 라운드.
5. 모든 라운드 통과 → `final_post.md` 확정.
6. **[MANDATORY HUMAN GATE]** 사용자에게 최종 포스트 전문·해시태그·첨부(링크/이미지)·
   가시성(PUBLIC/CONNECTIONS)·author URN을 그대로 출력하고 명시적 승인("게시", "publish",
   "OK" 등)을 받기 전까지 **절대 게시하지 말 것**. 평가 통과만으로는 게시 조건이 충족되지 않는다.
   승인 없이 `publish_linkedin.py`를 실행하면 안 된다.
7. 승인 후 LinkedIn UGC Posts API로 게시(아래 "게시" 절). 스크립트는 기본적으로
   `--yes` 플래그가 없으면 대화형 최종 확인을 한 번 더 받는다.

---

## 게시 (Publishing)

평가 통과 및 사용자 승인 이후에만 실행.

### 환경 변수

```bash
export LINKEDIN_ACCESS_TOKEN="Bearer용 access token (w_member_social scope)"
export LINKEDIN_AUTHOR_URN="urn:li:person:{member-id}"   # 개인 계정
# 또는
export LINKEDIN_AUTHOR_URN="urn:li:organization:{org-id}" # 회사 페이지 (w_organization_social 필요)
```

**Access Token 발급:**
1. [LinkedIn Developer Portal](https://www.linkedin.com/developers/)에서 앱 생성.
2. Products → **Share on LinkedIn** 또는 **Marketing Developer Platform** 추가.
3. OAuth 2.0 Authorization Code Flow로 `w_member_social`
   (회사 페이지는 `w_organization_social`) scope 포함 토큰 발급.
4. `/v2/userinfo` 또는 `/v2/me`로 `sub`/`id`를 받아 URN 구성
   (`urn:li:person:{sub}`).

### 스크립트

```bash
# 텍스트 포스트
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md

# 링크 포스트 (article preview)
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --link "https://example.com/article" \
  --link-title "Article Title" \
  --link-description "One-line description"

# 이미지 포스트 (로컬 이미지 업로드)
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md \
  --image /path/to/image.png \
  --image-alt "이미지 대체 텍스트"

# 드라이런 (요청 payload만 출력)
python3 ~/.claude/skills/linkedin-post-harness/scripts/publish_linkedin.py \
  --text-file linkedin-post/final_post.md --dry-run

# 가시성 (기본 PUBLIC)
#   --visibility PUBLIC | CONNECTIONS
```

### 게시 후
- 반환된 `post_urn`과 LinkedIn 공개 URL을 사용자에게 제공.
- `linkedin-post/publish_log.md`에 URN·시각·게시자 URN을 append.

---

## Working Directory & Output Requirements

- 작업 디렉토리: `linkedin-post/`
- 산출물: `spec.md`, `post_v1.md`…`post_vN.md`, `critique_v1.md`…,
  `handoff.md`, `final_post.md`, (게시 시) `publish_log.md`.
- 모든 파일은 Markdown. 수치 인용은 출처 명시, 미확인 시 `ASSUMPTION:` 라벨.
- Generator는 절대 자기 채점 금지. Evaluator 통과만이 다음 라운드 진입 조건.
- 실패 기준을 조용히 무시하지 말 것 — 표면화 후 해결.

---

## References

- 원문 전체 인벤토리 (예시·수치·사례 포함): [references/source-article-inventory.md](references/source-article-inventory.md)
- 포스트 유형별 템플릿·훅 패턴: [references/post-patterns.md](references/post-patterns.md)
- LinkedIn API 주의사항·Rate limit: [references/linkedin-api.md](references/linkedin-api.md)
