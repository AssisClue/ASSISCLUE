from __future__ import annotations

import re

from app.knowledge_library.models.chapter_view import ChapterView


_CHAPTER_RE = re.compile(
    r"(?im)^(chapter|cap[ií]tulo)\s+(\d+)\b[^\n\r]*"
)


class ChapterLocator:
    def locate(
        self,
        *,
        text: str,
        chapter_number: int | None = None,
        chapter_title_hint: str | None = None,
        max_chars: int | None = None,
    ) -> ChapterView | None:
        clean_text = str(text or "")
        if not clean_text.strip():
            return None

        matches = list(_CHAPTER_RE.finditer(clean_text))
        if not matches:
            return None

        target_index = None

        if chapter_number is not None:
            for idx, match in enumerate(matches):
                try:
                    if int(match.group(2)) == int(chapter_number):
                        target_index = idx
                        break
                except Exception:
                    continue

        if target_index is None and chapter_title_hint:
            hint = chapter_title_hint.strip().lower()
            for idx, match in enumerate(matches):
                title_line = match.group(0).strip().lower()
                if hint and hint in title_line:
                    target_index = idx
                    break

        if target_index is None:
            return None

        start = matches[target_index].start()
        end = matches[target_index + 1].start() if target_index + 1 < len(matches) else len(clean_text)
        chapter_text = clean_text[start:end].strip()

        if max_chars is not None and max_chars > 0:
            chapter_text = chapter_text[:max_chars]

        title = matches[target_index].group(0).strip()
        number = None
        try:
            number = int(matches[target_index].group(2))
        except Exception:
            number = None

        return ChapterView(
            chapter_number=number,
            chapter_title=title,
            start_index=start,
            end_index=end,
            text=chapter_text,
        )