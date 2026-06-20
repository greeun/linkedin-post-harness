#!/usr/bin/env python3
"""LinkedIn UGC Post publisher.

Publishes TEXT, ARTICLE (link preview), or IMAGE posts via LinkedIn v2 UGC Posts API.

Environment variables:
    LINKEDIN_ACCESS_TOKEN: OAuth2 bearer token with w_member_social
                          (or w_organization_social for company pages).
    LINKEDIN_AUTHOR_URN: Author URN, e.g. "urn:li:person:XXXX" or
                        "urn:li:organization:YYYY".

Safety:
    By default, the script prints the full payload and prompts for a typed
    "yes" before sending. Pass --yes to skip the prompt (e.g., when the
    human confirmation was already captured in the chat).
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


API_BASE = "https://api.linkedin.com/v2"


def _token() -> str:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        sys.exit("ERROR: LINKEDIN_ACCESS_TOKEN is not set")
    return token


def _author() -> str:
    author = os.environ.get("LINKEDIN_AUTHOR_URN")
    if not author or not author.startswith(("urn:li:person:", "urn:li:organization:")):
        sys.exit("ERROR: LINKEDIN_AUTHOR_URN must be set to a valid URN "
                 "(urn:li:person:... or urn:li:organization:...)")
    return author


def _headers(extra: dict | None = None) -> dict:
    h = {
        "Authorization": f"Bearer {_token()}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def _request(method: str, url: str, *, body: bytes | None = None,
             headers: dict | None = None) -> tuple[int, bytes, dict]:
    req = urllib.request.Request(url, data=body, method=method,
                                 headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read()
        sys.stderr.write(
            f"HTTP {e.code} {e.reason}\n{body.decode('utf-8', 'replace')}\n"
        )
        raise


def register_image_upload(author: str) -> tuple[str, str]:
    """Returns (asset_urn, upload_url)."""
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent",
            }],
        }
    }
    status, body, _ = _request(
        "POST",
        f"{API_BASE}/assets?action=registerUpload",
        body=json.dumps(payload).encode("utf-8"),
        headers=_headers(),
    )
    data = json.loads(body)
    value = data["value"]
    upload_url = (
        value["uploadMechanism"]
        ["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]
        ["uploadUrl"]
    )
    return value["asset"], upload_url


def upload_image_binary(upload_url: str, image_path: str) -> None:
    with open(image_path, "rb") as f:
        data = f.read()
    ctype, _ = mimetypes.guess_type(image_path)
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": ctype or "application/octet-stream",
    }
    _request("PUT", upload_url, body=data, headers=headers)


def build_payload(
    *,
    author: str,
    text: str,
    visibility: str,
    link: str | None,
    link_title: str | None,
    link_description: str | None,
    image_asset: str | None,
    image_alt: str | None,
) -> dict:
    share_content: dict = {
        "shareCommentary": {"text": text},
        "shareMediaCategory": "NONE",
    }

    if image_asset:
        share_content["shareMediaCategory"] = "IMAGE"
        media_entry: dict = {
            "status": "READY",
            "media": image_asset,
        }
        if image_alt:
            media_entry["description"] = {"text": image_alt}
        share_content["media"] = [media_entry]
    elif link:
        share_content["shareMediaCategory"] = "ARTICLE"
        media_entry = {"status": "READY", "originalUrl": link}
        if link_title:
            media_entry["title"] = {"text": link_title}
        if link_description:
            media_entry["description"] = {"text": link_description}
        share_content["media"] = [media_entry]

    return {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility,
        },
    }


def read_text(args: argparse.Namespace) -> str:
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    if args.text:
        return args.text
    sys.exit("ERROR: --text or --text-file is required")


def confirm_interactively(payload: dict) -> None:
    print("\n===== LinkedIn Post Preview =====\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print("\n=================================")
    print(f"Characters: {len(payload['specificContent']['com.linkedin.ugc.ShareContent']['shareCommentary']['text'])}")
    ans = input('\nPublish this post? type "yes" to confirm: ').strip().lower()
    if ans != "yes":
        sys.exit("Aborted by user.")


def main() -> None:
    p = argparse.ArgumentParser(description="Publish a LinkedIn UGC post.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Post body text (inline).")
    src.add_argument("--text-file", help="Path to post body file (e.g. final_post.md).")

    p.add_argument("--visibility", default="PUBLIC",
                   choices=["PUBLIC", "CONNECTIONS"])

    p.add_argument("--link", help="Article URL for link-preview post.")
    p.add_argument("--link-title", help="Preview title for link post.")
    p.add_argument("--link-description", help="Preview description for link post.")

    p.add_argument("--image", help="Local image path to upload.")
    p.add_argument("--image-alt", help="Alt text for the uploaded image.")

    p.add_argument("--dry-run", action="store_true",
                   help="Print payload only; do not call API.")
    p.add_argument("--yes", action="store_true",
                   help="Skip interactive confirmation (human already confirmed).")

    args = p.parse_args()

    if args.image and args.link:
        sys.exit("ERROR: --image and --link are mutually exclusive.")

    text = read_text(args)
    if len(text) > 3000:
        sys.exit(f"ERROR: text is {len(text)} chars (LinkedIn max 3000).")

    author = _author()

    image_asset: str | None = None
    upload_url: str | None = None
    if args.image:
        if args.dry_run:
            image_asset = "urn:li:digitalmediaAsset:DRYRUN"
        else:
            image_asset, upload_url = register_image_upload(author)

    payload = build_payload(
        author=author,
        text=text,
        visibility=args.visibility,
        link=args.link,
        link_title=args.link_title,
        link_description=args.link_description,
        image_asset=image_asset,
        image_alt=args.image_alt,
    )

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if not args.yes:
        confirm_interactively(payload)

    if args.image and upload_url:
        upload_image_binary(upload_url, args.image)
        time.sleep(3)  # let LinkedIn finalize the asset

    status, body, _ = _request(
        "POST",
        f"{API_BASE}/ugcPosts",
        body=json.dumps(payload).encode("utf-8"),
        headers=_headers(),
    )
    data = json.loads(body) if body else {}
    post_urn = data.get("id") or ""
    print(json.dumps({
        "status": status,
        "post_urn": post_urn,
        "url": _public_url(post_urn),
    }, ensure_ascii=False, indent=2))


def _public_url(post_urn: str) -> str:
    if not post_urn:
        return ""
    activity_id = post_urn.rsplit(":", 1)[-1]
    return f"https://www.linkedin.com/feed/update/{post_urn}/" \
        if post_urn.startswith("urn:li:share:") \
        else f"https://www.linkedin.com/feed/update/urn:li:activity:{activity_id}/"


if __name__ == "__main__":
    main()
