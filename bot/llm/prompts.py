"""All prompt templates in one place so tone/format stays consistent
across the vocabulary, paraphrase, writing and quiz engines."""

DAILY_VOCAB_PROMPT = """You are an IELTS English vocabulary teacher.
Generate exactly {count} useful, exam-relevant (IELTS Writing/Speaking Band 7+) English
vocabulary words or collocations. Avoid words already taught: {exclude_words}.

Return ONLY a JSON array, no prose, in this exact shape:
[
  {{
    "word": "mitigate",
    "part_of_speech": "verb",
    "definition": "short, simple definition in plain English",
    "example": "one natural example sentence using the word"
  }}
]
"""

DEFINE_WORDS_PROMPT = """You are an IELTS English vocabulary teacher.
For each of the following words/collocations, write a short, simple definition in
plain English and one natural example sentence (topic: IELTS-common topics).
Words: {words}

Return ONLY a JSON array, one object per word, in this exact shape and order:
[
  {{
    "word": "mitigate",
    "part_of_speech": "verb",
    "definition": "short, simple definition in plain English",
    "example": "one natural example sentence using the word"
  }}
]
"""

PARAPHRASE_SENTENCES_PROMPT = """You are an IELTS writing teacher.
Based on these vocabulary words: {words}, write {count} simple English sentences
(topic: everyday/IELTS common topics) that a student could rewrite (paraphrase)
using more advanced vocabulary or grammar structures.

Return ONLY a JSON array of strings, e.g.:
["Many people believe that technology has improved our lives.", "..."]
"""

PARAPHRASE_FEEDBACK_PROMPT = """You are an IELTS Writing examiner.
Original sentence: "{original}"
Student's paraphrase: "{answer}"

Evaluate the paraphrase. Return ONLY JSON in this shape:
{{
  "score": <integer 0-10>,
  "kept_meaning": <true/false>,
  "good_swaps": ["original phrase -> better phrase", "..."],
  "feedback": "1-2 short sentences of specific, encouraging feedback",
  "better_alternative": "a stronger Band 7+ paraphrase of the original sentence"
}}
"""

WRITING_SAMPLE_PROMPT = """You are an IELTS Writing Task 2 teacher.
Vocabulary to naturally weave in where possible: {words}.

1. Write one realistic IELTS Writing Task 2 question (opinion/discussion/problem-solution style).
2. Write ONE short sample paragraph (introduction OR one body paragraph, 3-5 sentences,
   Band 7.5-8 level) answering that question.
3. Annotate 4-6 notable spans in that paragraph: vocabulary, grammar structures,
   linking/argument devices, or useful phrases, each with a one-line explanation of
   why it's effective.

Return ONLY JSON in this shape:
{{
  "question": "the IELTS question",
  "sample_paragraph": "the paragraph text",
  "annotations": [
    {{"phrase": "significantly enhanced", "type": "vocabulary", "note": "strong academic collocation"}}
  ]
}}
"""

RECALL_QUIZ_PROMPT = """You are an English teacher creating an active-recall quiz.
Vocabulary: {words}
Today's paraphrase original sentence (for one recall question): "{paraphrase_sentence}"

Create {count} short recall questions mixing: word meaning, "use this word in a sentence",
and "paraphrase this sentence" tasks. Return ONLY JSON:
[
  {{"type": "meaning", "word": "mitigate", "question": "What does \\"mitigate\\" mean?"}},
  {{"type": "use", "word": "substantial", "question": "Write one sentence using \\"substantial\\"."}},
  {{"type": "paraphrase", "word": null, "question": "Paraphrase: Technology makes communication easier."}}
]
"""

GRADE_RECALL_ANSWER_PROMPT = """You are a supportive but precise English teacher.
Question: "{question}"
Expected focus word (if any): {word}
Student's answer: "{answer}"

Return ONLY JSON:
{{
  "is_correct": <true/false>,
  "feedback": "one short sentence of feedback",
  "correction": "corrected/model answer if the student's answer had an error, else empty string"
}}
"""

EXTRACT_MISTAKE_PROMPT = """You are an English grammar checker.
Student wrote: "{text}"

If there is a grammar/vocabulary mistake, return ONLY JSON:
{{"has_mistake": true, "wrong_text": "the exact wrong fragment", "corrected_text": "the fix", "reason": "short reason", "category": "one of: articles, prepositions, subject-verb-agreement, tense, word-choice, other"}}

If there is no mistake, return ONLY JSON:
{{"has_mistake": false}}
"""

WEEKLY_REPORT_SUMMARY_PROMPT = """You are an English learning coach writing a short,
encouraging weekly summary for a student.
Vocabulary mastered: {mastered}
Vocabulary still weak: {weak}
Frequent mistake categories: {mistake_categories}

Write a 2-3 sentence encouraging summary (plain text, no JSON) highlighting progress
and one concrete focus area for next week.
"""
