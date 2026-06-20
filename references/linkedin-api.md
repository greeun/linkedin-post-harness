# LinkedIn API Notes

## 사용하는 엔드포인트

**UGC Posts API** (v2)
- `POST https://api.linkedin.com/v2/ugcPosts` — 텍스트·링크·이미지 포스트 생성.

**Assets API** (이미지 업로드 2단계 플로우)
1. `POST https://api.linkedin.com/v2/assets?action=registerUpload` — 업로드 URL 발급.
2. 받은 `uploadUrl`에 `PUT`으로 바이너리 전송.
3. 반환된 `asset` URN을 UGC 포스트의 `media.media` 필드에 사용.

## 필수 헤더

```
Authorization: Bearer {ACCESS_TOKEN}
X-Restli-Protocol-Version: 2.0.0
LinkedIn-Version: 202405          # (Versioned API 사용 시)
Content-Type: application/json
```

## Scope

| Scope | 용도 |
|---|---|
| `w_member_social` | 개인 계정 포스트 |
| `w_organization_social` | 회사 페이지 포스트 (관리자 권한 필요) |
| `r_liteprofile` | `id`(member urn) 조회 |

## Author URN 형식

- 개인: `urn:li:person:{memberId}`
- 회사: `urn:li:organization:{orgId}`

## UGC Post 본체 예시 (텍스트)

```json
{
  "author": "urn:li:person:XXXX",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": { "text": "본문 ..." },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

## 링크 포스트

`shareMediaCategory: "ARTICLE"`, `media[0]`에 `{ status, originalUrl, title{text}, description{text} }`.

## 이미지 포스트

`shareMediaCategory: "IMAGE"`, `media[0].media` = asset URN.

## Rate Limits (2024 기준 알려진 값)

- 개인 포스트: 일 **125**건 정도(앱 전체 한도는 별도).
- 초과 시 `429` 반환. `Retry-After` 헤더 확인.

## 에러 주의

- `401`: 토큰 만료/scope 부족.
- `403`: 회사 페이지에 대한 관리 권한 없음.
- `422`: `author` URN 누락/형식 오류.
- 이미지 업로드 후 바로 posting하면 처리 중이라 실패할 수 있어 **2–5초 대기** 권장.

## LinkedIn 본문 규칙

- 최대 **3,000자**.
- URL은 본문에 포함되면 자동 미리보기가 생성되나, 링크 프리뷰 제어가 필요하면
  `ARTICLE` 미디어 카테고리를 사용.
- `@멘션`은 `shareCommentary.attributes`로 지정하는 별도 구조가 필요하여 본 스킬의
  기본 게시 플로우에는 포함하지 않는다.

## 참고 문서

- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/ugc-post-api
- https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/vector-asset-api
